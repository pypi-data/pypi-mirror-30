#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from random import choice
import string
import boto3

route53 = boto3.client('route53')
hosted_zone = os.environ['TRIPLECASK_CI_HOSTED_ZONE']

pool = string.ascii_lowercase + string.digits
generate_subdomain = lambda: ''.join([choice(pool) for _ in range(10)])


def _update_dns_records(mode, records):
    route53.change_resource_record_sets(
        HostedZoneId=hosted_zone,
        ChangeBatch={
            'Changes': [
                {
                    'Action': mode,
                    'ResourceRecordSet': {
                        'Name': record[0],
                        'Type': 'TXT',
                        'TTL': 60,
                        'ResourceRecords': [{'Value': record[1]}]
                    }
                } for record in records
            ]
        }
    )
