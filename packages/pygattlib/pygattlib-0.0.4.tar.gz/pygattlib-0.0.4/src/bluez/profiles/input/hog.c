/*
 *
 *  BlueZ - Bluetooth protocol stack for Linux
 *
 *  Copyright (C) 2012  Marcel Holtmann <marcel@holtmann.org>
 *  Copyright (C) 2012  Nordic Semiconductor Inc.
 *  Copyright (C) 2012  Instituto Nokia de Tecnologia - INdT
 *
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdlib.h>
#include <stdbool.h>
#include <errno.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <glib.h>

#include "lib/bluetooth.h"
#include "lib/sdp.h"
#include "lib/uuid.h"

#include "src/log.h"
#include "src/adapter.h"
#include "src/device.h"
#include "src/profile.h"
#include "src/service.h"
#include "src/shared/util.h"
#include "src/shared/uhid.h"
#include "src/shared/queue.h"
#include "src/plugin.h"

#include "suspend.h"
#include "attrib/att.h"
#include "attrib/gattrib.h"
#include "attrib/gatt.h"
#include "hog-lib.h"

#define HOG_UUID		"00001812-0000-1000-8000-00805f9b34fb"

struct hog_device {
	struct btd_device	*device;
	struct bt_hog		*hog;
};

static gboolean suspend_supported = FALSE;
static struct queue *devices = NULL;

static void hog_device_accept(struct hog_device *dev, struct gatt_db *db)
{
	char name[248];
	uint16_t vendor, product, version;

	if (dev->hog)
		return;

	if (device_name_known(dev->device))
		device_get_name(dev->device, name, sizeof(name));
	else
		strcpy(name, "bluez-hog-device");

	vendor = btd_device_get_vendor(dev->device);
	product = btd_device_get_product(dev->device);
	version = btd_device_get_version(dev->device);

	DBG("name=%s vendor=0x%X, product=0x%X, version=0x%X", name, vendor,
							product, version);

	dev->hog = bt_hog_new_default(name, vendor, product, version, db);
}

static struct hog_device *hog_device_new(struct btd_device *device)
{
	struct hog_device *dev;

	dev = new0(struct hog_device, 1);
	dev->device = btd_device_ref(device);

	if (!devices)
		devices = queue_new();

	queue_push_tail(devices, dev);

	return dev;
}

static void hog_device_free(void *data)
{
	struct hog_device *dev = data;

	queue_remove(devices, dev);
	if (queue_isempty(devices)) {
		queue_destroy(devices, NULL);
		devices = NULL;
	}

	btd_device_unref(dev->device);
	bt_hog_unref(dev->hog);
	free(dev);
}

static void set_suspend(gpointer data, gpointer user_data)
{
	struct hog_device *dev = data;
	gboolean suspend = GPOINTER_TO_INT(user_data);

	bt_hog_set_control_point(dev->hog, suspend);
}

static void suspend_callback(void)
{
	gboolean suspend = TRUE;

	DBG("Suspending ...");

	queue_foreach(devices, set_suspend, GINT_TO_POINTER(suspend));
}

static void resume_callback(void)
{
	gboolean suspend = FALSE;

	DBG("Resuming ...");

	queue_foreach(devices, set_suspend, GINT_TO_POINTER(suspend));
}

static int hog_probe(struct btd_service *service)
{
	struct btd_device *device = btd_service_get_device(service);
	const char *path = device_get_path(device);
	struct hog_device *dev;

	DBG("path %s", path);

	dev = hog_device_new(device);
	if (!dev)
		return -EINVAL;

	btd_service_set_user_data(service, dev);
	return 0;
}

static void hog_remove(struct btd_service *service)
{
	struct hog_device *dev = btd_service_get_user_data(service);
	struct btd_device *device = btd_service_get_device(service);
	const char *path = device_get_path(device);

	DBG("path %s", path);

	hog_device_free(dev);
}

static int hog_accept(struct btd_service *service)
{
	struct hog_device *dev = btd_service_get_user_data(service);
	struct btd_device *device = btd_service_get_device(service);
	struct gatt_db *db = btd_device_get_gatt_db(device);
	GAttrib *attrib = btd_device_get_attrib(device);

	if (!dev->hog) {
		hog_device_accept(dev, db);
		if (!dev->hog)
			return -EINVAL;
	}

	/* TODO: Replace GAttrib with bt_gatt_client */
	bt_hog_attach(dev->hog, attrib);

	btd_service_connecting_complete(service, 0);

	return 0;
}

static int hog_disconnect(struct btd_service *service)
{
	struct hog_device *dev = btd_service_get_user_data(service);

	bt_hog_detach(dev->hog);

	btd_service_disconnecting_complete(service, 0);

	return 0;
}

static struct btd_profile hog_profile = {
	.name		= "input-hog",
	.remote_uuid	= HOG_UUID,
	.device_probe	= hog_probe,
	.device_remove	= hog_remove,
	.accept		= hog_accept,
	.disconnect	= hog_disconnect,
	.auto_connect	= true,
};

static int hog_init(void)
{
	int err;

	err = suspend_init(suspend_callback, resume_callback);
	if (err < 0)
		error("Loading suspend plugin failed: %s (%d)", strerror(-err),
									-err);
	else
		suspend_supported = TRUE;

	return btd_profile_register(&hog_profile);
}

static void hog_exit(void)
{
	if (suspend_supported)
		suspend_exit();

	btd_profile_unregister(&hog_profile);
}

BLUETOOTH_PLUGIN_DEFINE(hog, VERSION, BLUETOOTH_PLUGIN_PRIORITY_DEFAULT,
							hog_init, hog_exit)
