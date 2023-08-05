#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NamedTuple


class DNS_01_Challenge(NamedTuple):
    raw: dict
    status: str
    token:   str
    uri: str
    dns_record_name: str
    dns_record_value: str
