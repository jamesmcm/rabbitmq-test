#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Receives and parses events, and executes query to update aggregate karma.

Logs warning and continues for invalid input
"""

import csv
import io
import logging
import sys

from connections import get_rabbitmq_connection,\
                        get_cassandra_connection


class AggregateKarmaUpdater:
    """
    Consumes events from the logs exchange and updates aggregate karma.

    The queue name is the first argument.

    It then parses the line as a csv, and runs the update_karma query
    which updates the aggregate karma of the crowdsourcer who submitted
    the vulnerability that was found.
    """

    def __init__(self, queue: str = 'cassandra'):
        """
        Initialise logger, redis connection and cursor, and the update query.

        Note we close the connection in __del__.
        """
        self.logger = logging.getLogger('rmqtest')
        self.queue_name = queue
        self.cassandra = get_cassandra_connection()

        crowdsourcer = self.cassandra.execute('SELECT id, name FROM crowdsourcer;')
        for d in crowdsourcer:
            q = f"UPDATE crowdsourcer_karma_distribution SET minor_sum = minor_sum + 0, medium_sum = medium_sum + 0, high_sum =  high_sum + 0, critical_sum = critical_sum + 0 WHERE cs_id = {d.id} AND cs_name = '{d.name}';"
            print(q)
            self.cassandra.execute(q)

    def callback(self, channel, method, properties, body) -> None:
        """
        Handle message from RabbitMQ queue.

        We read from the queue, parse the row as a csv,
        and run the update_karma query using the vulnerability ID found.

        :param channel: channel for RabbitMQ communication
        :param method: method for RabbitMQ message delivery
        :param properties: user-defined properties for message
        :param body: body of message from queue
        :return: None
        """
        csv_read = csv.reader(io.StringIO(body.decode("utf-8")))
        try:
            vuln_id = next(csv_read)[2]
            (sev_id, cs_id) = list(self.cassandra.execute(f"SELECT sev_id, cs_id FROM vulnerability WHERE id = {vuln_id}"))[0]
            (sev_name, sev_score) = list(self.cassandra.execute(f"SELECT severity, karma FROM severity WHERE id = {sev_id}"))[0]
            cs_name = list(self.cassandra.execute(f"SELECT name FROM crowdsourcer WHERE id = {cs_id}"))[0].name
            q = f"UPDATE crowdsourcer_karma_distribution SET {sev_name}_sum = {sev_name}_sum + {sev_score} WHERE cs_id = {cs_id} AND cs_name = '{cs_name}'"
            print(q)
            self.cassandra.execute(q)

        except IndexError:
            self.logger.warning("Not CSV: %s", body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self) -> None:
        """Read from queue until terminated."""
        with get_rabbitmq_connection() as connection:
            channel = connection.channel()

            channel.exchange_declare(exchange='logs',
                                     exchange_type='fanout')
            channel.queue_declare(queue=sys.argv[1], durable=True)

            channel.queue_bind(exchange='logs',
                               queue=self.queue_name)

            channel.basic_consume(sys.argv[1],
                                  self.callback,
                                  auto_ack=False)
            channel.start_consuming()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        queue_name = sys.argv[1]
    else:
        queue_name = 'cassandra'
    AggregateKarmaUpdater(queue=queue_name).run()
