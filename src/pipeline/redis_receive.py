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

import MySQLdb.cursors

from connections import get_db_connection, get_rabbitmq_connection,\
                        get_redis_connection


class AggregateKarmaUpdater:
    """
    Consumes events from the logs exchange and updates aggregate karma.

    The queue name is the first argument.

    It then parses the line as a csv, and runs the update_karma query
    which updates the aggregate karma of the crowdsourcer who submitted
    the vulnerability that was found.
    """

    def __init__(self, queue: str = 'redis'):
        """
        Initialise logger, redis connection and cursor, and the update query.

        Note we close the connection in __del__.
        """
        self.logger = logging.getLogger('rmqtest')
        self.queue_name = queue
        self.redis = get_redis_connection()
        self.mysql_conn = get_db_connection()
        self.cursor = self.mysql_conn.cursor(MySQLdb.cursors.DictCursor)

        self.cursor.execute('SELECT * FROM crowdsourcer;')
        crowdsourcer = self.cursor.fetchall()
        for d in crowdsourcer:
            self.redis.hset('crowdsourcer', d['id'], d['name'])
            self.redis.hset('output', str(d['id'])+'_minor', 0)
            self.redis.hset('output', str(d['id'])+'_medium', 0)
            self.redis.hset('output', str(d['id'])+'_high', 0)
            self.redis.hset('output', str(d['id'])+'_critical', 0)

        self.cursor.execute('SELECT * FROM severity;')
        severity = self.cursor.fetchall()
        for d in severity:
            self.redis.hset('severity_name', d['id'], d['severity'])
            self.redis.hset('severity', d['id'], d['karma'])

        self.cursor.execute('SELECT * FROM vulnerability;')
        vulnerability = self.cursor.fetchall()
        for d in vulnerability:
            self.redis.hset('vulnerability_cs', d['id'], d['cs_id'])
            self.redis.hset('vulnerability_sev', d['id'], d['sev_id'])

        self.cursor.close()
        self.mysql_conn.close()

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
            cs_id = self.redis.hget('vulnerability_cs', vuln_id)
            sev_id = self.redis.hget('vulnerability_sev', vuln_id)
            sev_score = self.redis.hget('severity', sev_id)
            sev_name = self.redis.hget('severity_name', sev_id)
            self.redis.hincrby('output', str(cs_id)+'_'+str(sev_name), int(sev_score))

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
        queue_name = 'redis'
    AggregateKarmaUpdater(queue=queue_name).run()
