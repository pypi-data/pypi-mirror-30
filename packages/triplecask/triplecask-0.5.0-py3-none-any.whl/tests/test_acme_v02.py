#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import urllib.request
import time
from triplecask import crypto
from triplecask.acme_v02.acme import ACME
from tests.helper import generate_subdomain, _update_dns_records

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


def certificate_request_rigmarole(domains):
    if acme_client.kid is None:
        acme_client.register()

    order = acme_client.new_order(domains)

    _update_dns_records(
        'UPSERT',
        [(c.dns_record_name, c.dns_record_value) for c in order.challenges]
    )

    time.sleep(30)

    for challenge in order.challenges:
        acme_client.validate_challenge(challenge)

        while challenge.status == 'pending':
            time.sleep(1.5)
            challenge = acme_client.refresh_challenge(challenge)

        assert challenge.status == 'valid'

    _update_dns_records(
        'DELETE',
        [(c.dns_record_name, c.dns_record_value) for c in order.challenges]
    )

    domain_key = crypto.generate_private_key()
    csr = crypto.generate_certificate_request(domains, domain_key)

    order = acme_client.finalize_order(order, csr)

    while order.status == 'pending':
        time.sleep(2)
        order = acme_client.refresh_order(order)

    assert order.status == 'valid'

    return acme_client.certificate_chain_for_order(order)


def test_request_single_domain_certificate():
    domain_name = f'{generate_subdomain()}.{domain}'

    certificate_chain = certificate_request_rigmarole([domain_name])

    assert len(certificate_chain) > 0

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'
    assert re.match(pattern, certificate_chain, flags=re.DOTALL) is not None


def test_request_san_certificate():
    domain_names = [f'{generate_subdomain()}.{domain}' for _ in range(3)]

    certificate_chain = certificate_request_rigmarole(domain_names)

    assert len(certificate_chain) > 0

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'
    assert re.match(pattern, certificate_chain, flags=re.DOTALL) is not None


def test_request_wildcard_certificate():
    domain_name = f'*.{generate_subdomain()}.{domain}'

    certificate_chain = certificate_request_rigmarole([domain_name])

    assert len(certificate_chain) > 0

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'
    assert re.match(pattern, certificate_chain, flags=re.DOTALL) is not None


def test_request_wildcard_san_certificate():
    domain_names = [f'{generate_subdomain()}.{domain}' for _ in range(2)]
    domain_names.append(f'*.{generate_subdomain()}.{domain}')

    certificate_chain = certificate_request_rigmarole(domain_names)

    assert len(certificate_chain) > 0

    pattern = r'-----BEGIN CERTIFICATE-----.*-----END CERTIFICATE-----'
    assert re.match(pattern, certificate_chain, flags=re.DOTALL) is not None
