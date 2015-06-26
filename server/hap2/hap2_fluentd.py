#! /usr/bin/env python
# coding: UTF-8
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
import haplib
import standardhap
import subprocess
import logging
import multiprocessing
import datetime

class Hap2FluentdMain(haplib.BaseMainPlugin):

    def __init__(self, *args, **kwargs):
        haplib.BaseMainPlugin.__init__(self, kwargs["transporter_args"])
        self.__manager = None

    def set_ms_info(self, ms_info):
        if self.__manager is not None:
            return
        manager = multiprocessing.Process(target=self.__fluentd_manager_main)
        manager.daemon = True
        manager.start()

    def __fluentd_manager_main(self):
        # TODO: add action when the sub proccess is unexpectedly terminated.
        logging.info("Started fluentd manger process.")
        # TODO: argument list should be created from monitoring server info.
        fluentd_args = ["td-agent", "--suppress-config-dump",   
                        "-c", "td-agent.conf"]

        # TODO: handle when the launch failed.
        fluentd = subprocess.Popen(fluentd_args, stdout=subprocess.PIPE)

        while True:
            line = fluentd.stdout.readline()
            timestamp, tag, msg = self.__parse_line(line)
            self.__put_event(timestamp, tag, msg)

    def __put_event(self, timestamp, tag, msg):
        # TODO: calculate event_id
        last_info = self.get_cached_event_last_info()
        event_id = "1"

        # TODO parse msg to determine the following parameters.
        hapi_event_type = "NOTIFICATION"
        hapi_status = "UNKNOWN"
        hapi_severity = "UNKNOWN"

        events = []
        events.append({
            "eventId": event_id,
            "time": haplib.Utils.conv_to_hapi_time(timestamp),
            "type": hapi_event_type,
            "status": hapi_status,
            "severity": hapi_severity,
            "hostId": "0",
            "hostName": "N/A",
            "brief": msg,
            "extendedInfo": ""
        })
        self.put_events(events)

    def __parse_line(self, line):
        # TODO: handle exception due to the unexpected form of input
        header, msg = line.split(": ", 1)
        timestamp, tag = self.__parse_header(header)
        return timestamp, tag, msg

    def __parse_header(self, header):
        LEN_DATE_TIME = 19
        timestamp = datetime.datetime.strptime(header[:LEN_DATE_TIME],
                                               "%Y-%m-%d %H:%M:%S")
        IDX_OFS_SIGN = LEN_DATE_TIME + 1
        IDX_OFS_HOUR = IDX_OFS_SIGN + 1
        IDX_OFS_MINUTE = IDX_OFS_HOUR + 2
        offset_sign = header[IDX_OFS_SIGN]
        offset_hour = int(header[IDX_OFS_HOUR:IDX_OFS_HOUR+2])
        offset_hour *= {"+": 1, "-": -1}[offset_sign]
        offset_minute = int(header[IDX_OFS_MINUTE:IDX_OFS_MINUTE+2])

        offset = datetime.timedelta(hours=offset_hour, minutes=offset_hour)
        utc_timestamp = timestamp - offset

        IDX_HEADER_BEGIN = IDX_OFS_MINUTE + 1
        tag = header[IDX_HEADER_BEGIN:]
        return utc_timestamp, tag

class Hap2Fluentd(standardhap.StandardHap):
    def create_main_plugin(self, *args, **kwargs):
        return Hap2FluentdMain(*args, **kwargs)

if __name__ == '__main__':
    hap = Hap2Fluentd()
    hap()
