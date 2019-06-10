#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Define connection functions for MariaDB and RabbitMQ.

Here we hard-code credentials, in production this should be handled by
a secrets manager or at least a separate file never committed to git.
"""

from cassandra.cluster import Cluster
from time import sleep

import MySQLdb
import MySQLdb.cursors
import pika
import redis


def get_cassandra_connection(retries=15, sleep_time=2):
    """Get connection to cassandra."""
    tries = 0
    while True:
        try:
            cluster = Cluster(['cassandra'], port=9042)
            session = cluster.connect()
            session.execute("USE rmqtest;")
            return session
        except Exception as e:
            print(e)
            if tries > retries:
                raise ConnectionError('Cannot connect to cassandra server')
            sleep(sleep_time)


def get_redis_connection(retries=15, sleep_time=1):
    """Get connection to Redis."""
    tries = 0
    while True:
        try:
            return redis.Redis(
                            host='redis',
                            charset="utf-8",
                            decode_responses=True,
                            port=6379)
        except ConnectionError:
            if tries > retries:
                raise ConnectionError('Cannot connect to redis server')
            sleep(sleep_time)


def get_db_connection(retries=15, sleep_time=1):
    """Get connection to MariaDB."""
    tries = 0
    while True:
        try:
            return MySQLdb.connect(
                host='db',
                user='root',
                passwd='groot',
                db='rmqtest',
                connect_timeout=30,
                use_unicode=True,
                charset='utf8',
                autocommit=True
            )

        except ConnectionError:
            if tries > retries:
                raise ConnectionError('Cannot connect to MariaDB server')
            sleep(sleep_time)


def get_rabbitmq_connection(retries=15, sleep_time=1):
    """
    Get connection to RabbitMQ.

    Will retry 15 times by default,
    with a sleep time of 1 second between tries.
    """
    tries = 0
    while True:
        try:
            return pika.BlockingConnection(
                pika.ConnectionParameters(
                    host='rabbit'
                )
            )

        except pika.exceptions.AMQPConnectionError:
            if tries > retries:
                raise pika.exceptions.AMQPConnectionError(
                    'Cannot connect to rabbitmq server'
                )
            sleep(sleep_time)
