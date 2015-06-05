#! /usr/bin/env python
"""
  Copyright (C) 2015 Project Hatohol

  This file is part of Hatohol.

  Hatohol is free software: you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License, version 3
  as published by the Free Software Foundation.

  Hatohol is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with Hatohol. If not, see
  <http://www.gnu.org/licenses/>.
"""

import multiprocessing
import argparse
import logging
import time
import sys
import traceback
import imp

class StandardHap:

    DEFAULT_ERROR_SLEEP_TIME = 10

    def __init__(self):
        self.__error_sleep_time = self.DEFAULT_ERROR_SLEEP_TIME

        parser = argparse.ArgumentParser()

        choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        parser.add_argument("--log", dest="loglevel", choices=choices,
                            default="INFO")
        parser.add_argument("--amqp-broker", type=str,
                            default="localhost")
        parser.add_argument("--amqp-port", type=int, default=5672)
        parser.add_argument("--amqp-vhost", type=str,
                            default="hatohol")
        parser.add_argument("--amqp-queue", type=str,
                            default="standardhap-queue")
        parser.add_argument("--amqp-user", type=str, default="hatohol")
        parser.add_argument("--amqp-password", type=str, default="hatohol")
        parser.add_argument("--transporter", type=str,
                            default="RabbitMQHapiConnector")
        parser.add_argument("--transporter-module", type=str, default="haplib")

        self.__parser = parser
        self.__main_plugin = None

    def get_argument_parser(self):
        return self.__parser

    def get_main_plugin(self):
        return self.__main_plugin

    """
    An abstract method to create main plugin process.
    A sub class shall implement this method, or the default implementation
    raises AssertionError.

    @return
    A main plugin. The class shall be callable.
    """
    def create_main_plugin(self, *args, **kwargs):
        raise NotImplementedError

    """
    An abstract method to create poller plugin process.

    @return
    An poller plugin. The class shall be callable.
    If this method returns None, no poller process is created.
    The default implementation returns None.
    """
    def create_poller(self, sender):
        return None

    def on_parsed_argument(self, args):
        pass

    def on_got_monitoring_server_info(self, ms_info):
        pass

    def __setup_logging_level(self, args):
        numeric_level = getattr(logging, args.loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)

    def __parse_argument(self):
        args = self.__parser.parse_args()
        self.__setup_logging_level(args)

        self.on_parsed_argument(args)
        return args

    def __call__(self):
        while True:
            try:
                self.__run()
            except KeyboardInterrupt:
                break
            except (AssertionError, SystemExit):
                raise
            except:
                (ty, val, tb) = sys.exc_info()
                logging.error("type: " + str(ty) + ", value: " + str(val) + "\n"
                              + traceback.format_exc())
            else:
                break
            logging.info("Rerun after %d sec" % self.__error_sleep_time)
            time.sleep(self.__error_sleep_time)

    def __launch_poller(self, sender):
        poller = self.create_poller(sender)
        if poller is None:
            return
        logging.info("created poller plugin.")
        poll_process = multiprocessing.Process(target=poller)
        poll_process.daemon = True
        poll_process.start()

    def __run(self):
        args = self.__parse_argument()
        logging.info("Transporter: %s" % args.transporter)

        # load module for the transporter
        (file, pathname, descr) = imp.find_module(args.transporter_module)
        mod = imp.load_module("", file, pathname, descr)
        transporter_class = eval("mod.%s" % args.transporter)

        # TODO: arguments should be pushed by each transporter
        transporter_args = {"class": transporter_class,
                            "amqp_broker": args.amqp_broker,
                            "amqp_port": args.amqp_port,
                            "amqp_vhost": args.amqp_vhost,
                            "amqp_queue": args.amqp_queue,
                            "amqp_user": args.amqp_user,
                            "amqp_password": args.amqp_password}
        self.__main_plugin = self.create_main_plugin(transporter_args=transporter_args)
        logging.info("created main plugin.")

        ms_info = self.__main_plugin.get_monitoring_server_info()
        logging.info("got monitoring server info.")
        self.on_got_monitoring_server_info(ms_info)

        self.__launch_poller(self.__main_plugin.get_sender())
        logging.info("launched poller plugin.")

        self.__main_plugin()
