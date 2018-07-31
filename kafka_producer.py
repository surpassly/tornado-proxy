#!/usr/bin/env python
# encoding: utf-8

from kafka import KafkaProducer
from kafka.errors import KafkaError

conf = {
    "bootstrap_servers": [
        'yz1522.kafka.data.sina.com.cn:9110',
        'yz1526.kafka.data.sina.com.cn:9110',
        'yz1525.kafka.data.sina.com.cn:9110',
        'yz1527.kafka.data.sina.com.cn:9110',
        'yz1521.kafka.data.sina.com.cn:9110'
    ],
    "topic_name": 'sina_cms_spider_feed',
    "sasl_plain_username": 'sina_cms_spider',
    "sasl_plain_password": 'ab017749a63fe9b85e4a131524656693'
}

producer = KafkaProducer(bootstrap_servers=conf['bootstrap_servers'],
                         sasl_mechanism="PLAIN",
                         security_protocol='SASL_PLAINTEXT',
                         api_version=(0, 10),
                         retries=5,
                         sasl_plain_username=conf['sasl_plain_username'],
                         sasl_plain_password=conf['sasl_plain_password'])

partitions = producer.partitions_for(conf['topic_name'])
print 'Topic下分区: %s' % partitions

try:
    future = producer.send(conf['topic_name'], 'test')
    future.get()
    print 'send message succeed.'
except KafkaError, e:
    print 'send message failed.'
    print e
