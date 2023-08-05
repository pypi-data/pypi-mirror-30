#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import urllib.request
import time
from triplecask.acme_v01.acme import ACME
from triplecask import crypto
from tests.helper import _update_dns_records, generate_subdomain

domain = os.environ['TRIPLECASK_CI_DOMAIN']
acme_client = ACME(ACME.create_account_key())


def test_create_account_key():
    private_key = ACME.create_account_key()

    pattern = r'-----BEGIN (?:RSA )?PRIVATE KEY-----.*-----END (?:RSA )?PRIVATE KEY-----'
    assert re.match(pattern, private_key, flags=re.DOTALL) is not None


def test_account_registration():
    acme = ACME(ACME.create_account_key())

    r = json.loads(acme.register())

    expected_keys = ['agreement', 'contact', 'createdAt', 'id', 'initialIp',
                     'key', 'status']

    checkip_endpoint = 'http://checkip.amazonaws.com'

    assert set(expected_keys).issubset(r.keys())

    assert r['status'] == 'valid'
    assert r['key']['kty'] == 'RSA'
    assert r['initialIp'] == urllib.request.urlopen(
        checkip_endpoint).read().strip().decode('utf-8')


def test_duplicate_account_registration():
    private_key = ACME.create_account_key()
    acme = ACME(private_key)

    r = json.loads(acme.register())

    expected_keys = ['agreement', 'contact', 'createdAt', 'id', 'initialIp',
                     'key', 'status']

    assert set(expected_keys).issubset(r.keys())

    acme = ACME(private_key)

    r = acme.register()

    assert r is None


def test_request_dns_challenge():
    acme = ACME(ACME.create_account_key())
    acme.register()

    domain_name = f'{generate_subdomain()}.{domain}'
    challenge = acme.request_dns_challenge(domain_name)

    expected_keys = ['type', 'status', 'uri', 'token']

    assert type(challenge.raw) == dict
    assert set(expected_keys).issubset(challenge.raw.keys())
    assert challenge.raw['type'] == 'dns-01'
    assert challenge.raw['status'] == challenge.status == 'pending'
    assert len(challenge.raw['uri']) > 0
    assert challenge.uri == challenge.raw['uri']
    assert len(challenge.raw['token']) > 0
    assert challenge.token == challenge.raw['token']
    assert len(challenge.dns_record_value) > 0
    assert challenge.dns_record_name == f'_acme-challenge.{domain_name}.'


def certificate_request_rigmarole(domains):
    acme_client.register()

    challenges = {n: acme_client.request_dns_challenge(n) for n in domains}

    _update_dns_records(
        'UPSERT',
        [(c.dns_record_name, c.dns_record_value) for c in challenges.values()]
    )

    time.sleep(30)

    for challenge in challenges.values():
        acme_client.validate_challenge(challenge)

        while challenge.status == 'pending':
            time.sleep(1.5)
            challenge = acme_client.refresh_challenge(challenge)

        assert challenge.status == 'valid'

    _update_dns_records(
        'DELETE',
        [(c.dns_record_name, c.dns_record_value) for c in challenges.values()]
    )

    domain_key = crypto.generate_private_key()
    csr = crypto.generate_certificate_request(domains, domain_key)

    return acme_client.request_certificate_for_csr(csr)


def test_request_single_domain_certificate():
    domain_name = f'{generate_subdomain()}.{domain}'

    certificate, intermediary_certificate = certificate_request_rigmarole([domain_name])

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'

    assert re.match(pattern, certificate, flags=re.DOTALL) is not None
    assert re.match(pattern, intermediary_certificate, flags=re.DOTALL) is not None


def test_request_san_certificate():
    domain_names = [f'{generate_subdomain()}.{domain}' for _ in range(3)]

    certificate, intermediary_certificate = certificate_request_rigmarole(domain_names)

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'

    assert re.match(pattern, certificate, flags=re.DOTALL) is not None
    assert re.match(pattern, intermediary_certificate, flags=re.DOTALL) is not None
