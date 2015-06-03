#!/usr/bin/env python
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

import logging
import pika
from transporter import Transporter

class RabbitMQConnector(Transporter):

    def __init__(self):
        Transporter.__init__(self)
        self._channel = None

    def setup(self, transporter_args):
        """
        @param transporter_args
        The following keys shall be included.
        - amqp_broker     A broker IP or FQDN.
        - amqp_port       A broker port.
        - amqp_vhost      A virtual host.
        - amqp_queue      A queue name.
        - amqp_user       A user name.
        - amqp_password   A password.
        """

        broker = transporter_args["amqp_broker"]
        port = transporter_args["amqp_port"]
        vhost = transporter_args["amqp_vhost"]
        queue_name = transporter_args["amqp_queue"]
        user_name = transporter_args["amqp_user"]
        password = transporter_args["amqp_password"]

        logging.debug("Called stub method: call().");
        self._queue_name = queue_name
        credentials = pika.credentials.PlainCredentials(user_name, password)
        param = pika.connection.ConnectionParameters(host=broker, port=port,
                                                     virtual_host=vhost,
                                                     credentials=credentials)
        connection = pika.adapters.blocking_connection.BlockingConnection(param)
        self._channel = connection.channel()
        self._channel.queue_declare(queue=queue_name)

    def call(self, msg):
        self._publish(msg)

    def reply(self, msg):
        self._publish(msg)

    def run_receive_loop(self):
        assert self._channel != None

        self._channel.basic_consume(self._consume_handler,
                                    queue=self._queue_name, no_ack=True)
        self._channel.start_consuming()

    def _consume_handler(self, ch, method, properties, body):
        receiver = self.get_receiver()
        if receiver is None:
            logging.warning("Receiver is not registered.")
            return
        receiver(self._channel, body)

    def _publish(self, msg):
        self._channel.basic_publish(exchange="", routing_key=self._queue_name,
                                    body=msg)

