/*
 *
 *  BlueZ - Bluetooth protocol stack for Linux
 *
 *  Copyright (C) 2018  Intel Corporation
 *
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdbool.h>
#include <signal.h>
#include <sys/signalfd.h>

#include <glib.h>

#include "mainloop.h"

static GMainLoop *main_loop;
static int exit_status;

void mainloop_init(void)
{
	main_loop = g_main_loop_new(NULL, FALSE);
}

void mainloop_quit(void)
{
	if (!main_loop)
		return;

	g_main_loop_quit(main_loop);
}

void mainloop_exit_success(void)
{
	exit_status = EXIT_SUCCESS;
	mainloop_quit();
}

void mainloop_exit_failure(void)
{
	exit_status = EXIT_FAILURE;
	mainloop_quit();
}

int mainloop_run(void)
{
	if (!main_loop)
		return -EINVAL;

	g_main_loop_run(main_loop);

	g_main_loop_unref(main_loop);
	main_loop = NULL;

	return exit_status;
}

int mainloop_add_fd(int fd, uint32_t events, mainloop_event_func callback,
				void *user_data, mainloop_destroy_func destroy)
{
	return -ENOSYS;
}

int mainloop_modify_fd(int fd, uint32_t events)
{
	return -ENOSYS;
}

int mainloop_remove_fd(int fd)
{
	return -ENOSYS;
}

int mainloop_add_timeout(unsigned int msec, mainloop_timeout_func callback,
				void *user_data, mainloop_destroy_func destroy)
{
	return -ENOSYS;
}

int mainloop_modify_timeout(int fd, unsigned int msec)
{
	return -ENOSYS;
}

int mainloop_remove_timeout(int id)
{
	return -ENOSYS;
}

int mainloop_set_signal(sigset_t *mask, mainloop_signal_func callback,
				void *user_data, mainloop_destroy_func destroy)
{
	return -ENOSYS;
}
