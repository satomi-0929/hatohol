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
import haplib

class StandardHap:

    DEFAULT_ERROR_SLEEP_TIME = 10

    def __init__(self):
        self.__error_sleep_time = self.DEFAULT_ERROR_SLEEP_TIME

        parser = argparse.ArgumentParser()

        choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        parser.add_argument("--log", dest="loglevel", choices=choices,
                            default="INFO")
        haplib.Utils.define_transporter_arguments(parser)

        self.__parser = parser
        self.__main_plugin = None

    def get_argument_parser(self):
        return self.__parser

    def get_main_plugin(self):
        return self.__main_plugin

    def get_poller(self):
        return self.__poller

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
    def create_poller(self, *args, **kwargs):
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
            #TODO: make sure poller and receiver has been killed.
            logging.info("Rerun after %d sec" % self.__error_sleep_time)
            time.sleep(self.__error_sleep_time)

    def __create_poller(self, sender, dispatcher):
        POLLER_COMPONENT_CODE = 0x20
        poller = self.create_poller(sender=sender,
                                    process_id="Poller",
                                    component_code=POLLER_COMPONENT_CODE)
        if poller is None:
            return
        logging.info("created poller plugin.")
        dispatcher.attach_destination(poller.get_reply_queue(), "Poller")
        return poller

    def __start_poller(self, poller):
        if poller is None:
            return
        poll_process = multiprocessing.Process(target=poller)
        poll_process.daemon = True
        poll_process.start()

    def __run(self):
        args = self.__parse_argument()
        logging.info("Transporter: %s" % args.transporter)
        transporter_class = haplib.Utils.load_transporter(args)
        transporter_args = {"class": transporter_class}
        transporter_args.update(transporter_class.parse_arguments(args))

        self.__main_plugin = self.create_main_plugin(transporter_args=transporter_args)
        logging.info("created main plugin.")

        self.__poller = self.__create_poller(self.__main_plugin.get_sender(),
                                             self.__main_plugin.get_dispatcher())

        self.__main_plugin.start_dispatcher()
        logging.info("started dispatcher process.")
        self.__main_plugin.start_receiver()
        logging.info("started receiver process.")

        ms_info = self.__main_plugin.get_monitoring_server_info()
        logging.info("got monitoring server info.")
        self.on_got_monitoring_server_info(ms_info)

        self.__start_poller(self.__poller)
        logging.info("started poller plugin.")

        self.__main_plugin()
