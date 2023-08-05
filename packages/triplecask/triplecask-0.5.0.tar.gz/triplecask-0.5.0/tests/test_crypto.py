#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
from random import choice
import re
import string
from triplecask import crypto
from nose.tools import raises
import importlib.util
from tests.helper import generate_subdomain

PyOpenSSL_AVAILABLE = importlib.util.find_spec('OpenSSL') is not None

domain = os.environ['TRIPLECASK_CI_DOMAIN']


def test_generate_private_key():
    private_key = crypto.generate_private_key()

    if PyOpenSSL_AVAILABLE:
        pattern = r'-----BEGIN PRIVATE KEY-----.*-----END PRIVATE KEY-----'
    else:
        pattern = r'-----BEGIN RSA PRIVATE KEY-----.*-----END RSA PRIVATE KEY-----'
    assert re.match(pattern, private_key, flags=re.DOTALL) is not None


@raises(Exception)
def test_generate_private_key_invalid_size():
    crypto.generate_private_key(size='2049')


def test_generate_certificate_request_single_domain():
    private_key = crypto.generate_private_key()

    domain_name = f'{generate_subdomain()}.{domain}'

    csr = crypto.generate_certificate_request([domain_name], private_key)

    pattern = r'-----BEGIN CERTIFICATE REQUEST-----.*-----END CERTIFICATE REQUEST-----'
    assert re.match(pattern, csr, flags=re.DOTALL) is not None


def test_generate_certificate_request_multiple_domains():
    private_key = crypto.generate_private_key()

    domain_names = [f'{generate_subdomain()}.{domain}' for _ in range(5)]

    csr = crypto.generate_certificate_request(domain_names, private_key)

    pattern = r'-----BEGIN CERTIFICATE REQUEST-----.*-----END CERTIFICATE REQUEST-----'
    assert re.match(pattern, csr, flags=re.DOTALL) is not None


def test_parse_private_key():
    private_key = crypto.generate_private_key()

    modulus, exponent = crypto.parse_private_key(private_key)

    assert re.match(r'^[a-f0-9:\s]*$', modulus) is not None
    assert re.match(r'[01]*', exponent)


def test_sign_data():
    private_key = crypto.generate_private_key()

    signed_data = crypto.sign(private_key, 'hello world')

    assert type(signed_data) == bytes
    assert len(signed_data) > 0


def test_der_encode_csr():
    private_key = crypto.generate_private_key()

    domain_name = f'{generate_subdomain()}.{domain}'
    csr = crypto.generate_certificate_request([domain_name], private_key)

    der_encoded_csr = crypto.der_encode_csr(csr)

    assert type(der_encoded_csr) == bytes
    assert len(der_encoded_csr) > 0
