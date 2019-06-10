#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate finding events.

Read input passed from tailing finding.csv and send it to
a RabbitMQ exchange named logs.
"""

import sys

import pika

from connections import get_rabbitmq_connection


class EventGenerator:
    """
    Forwards stdin to logs exchange.

    Reads standard input by line,
    then sends them to a RabbitMQ exchange named logs.

    Methods
    -------
        run()
    """

    @staticmethod
    def run() -> None:
        """Loops over standard input until EOF or terminated."""
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()
            channel.exchange_declare(exchange='logs',
                                     exchange_type='fanout')

            for line in sys.stdin:
                channel.basic_publish(exchange='logs',
                                      routing_key='hello',
                                      body=line,
                                      properties=pika.BasicProperties(
                                          delivery_mode=2,
                                      )
                                      )


if __name__ == '__main__':
    EventGenerator().run()
