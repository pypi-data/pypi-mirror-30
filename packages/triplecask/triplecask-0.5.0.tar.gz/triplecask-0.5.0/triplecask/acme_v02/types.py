#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import NamedTuple


class DNS_01_Challenge(NamedTuple):
    raw: dict
    status: str
    token:   str
    refresh_uri: str
    finalize_uri: str
    dns_record_name: str
    dns_record_value: str


class Order(NamedTuple):
    raw: dict
    status: str
    domains: list
    expires: str
    challenges: list
    certificate_uri: str
    refresh_uri: str
    finalize_uri: str
