#!/usr/bin/env python3
# -*- coding: utf8 -*-

import base64
import binascii
import copy
import hashlib
import json
import os
import re
import textwrap
import urllib.request
import urllib.error
from triplecask import crypto
from triplecask.dns_challenge import DNS_01_Challenge

STAGING_DIRECTORY_URI = 'https://acme-staging.api.letsencrypt.org/directory'
PRODUCTION_DIRECTORY_URI = 'https://acme-v01.api.letsencrypt.org/directory'


class ACMEv01(object):

    _b64 = lambda _, x: base64.urlsafe_b64encode(x).decode('utf-8').rstrip('=')

    def __init__(self, account_key, directory_uri=STAGING_DIRECTORY_URI):
        """
        Creates a new ACME client instance for a given private key.
        """

        self.account_key = account_key

        r = urllib.request.urlopen(directory_uri)

        self.endpoints = json.load(r)
        self.nonce = r.getheader('Replay-Nonce', None)
        self.pub_key_modulus, self.pub_key_exponent = crypto.parse_private_key(
            self.account_key)

    @staticmethod
    def create_account_key():
        """
        Creates a new account key
        """

        return crypto.generate_private_key()

    def __http_post(self, uri, payload=None, uri_mode='directory_resource'):
        """
        Make a POST request to the ACME API
        """
        if uri_mode == 'directory_resource':
            uri = self.endpoints.get(uri)
        elif uri_mode == 'uri':
            pass
        else:
            raise ValueError(f'Invalid value for uri_mode: {uri_mode}')

        try:
            resp = urllib.request.urlopen(
                uri, self.__sign_request(payload).encode('utf-8'))
        except urllib.error.HTTPError as httperror:
            resp = httperror

        self.nonce = resp.getheader("Replay-Nonce", None)

        return resp.getcode(), resp.read(), resp.getheaders()

    @property
    def __jws_header(self):
        """
        Returns the JOSE JWS to use when making authenticated
        requests to the ACME API host
        """

        if '_jws_header' not in self.__dict__:
            self._jws_header = {
                'alg': 'RS256',
                'jwk': {
                    'kty': 'RSA',
                    'e': self._b64(binascii.unhexlify(
                                self.pub_key_exponent.encode('utf-8'))),
                    'n': self._b64(binascii.unhexlify(re.sub(
                        r'(\s|:)', '', self.pub_key_modulus).encode('utf-8')
                    ))
                }
            }

        return self._jws_header

    @property
    def __thumbprint(self):
        """
        Returns the thumbprint to use when handling DNS
        validation challenges.
        """

        if '_thumbprint' not in self.__dict__:
            self._thumbprint = self._b64(hashlib.sha256(
                json.dumps(self.__jws_header['jwk'], sort_keys=True,
                           separators=(',', ':')).encode('utf-8')
            ).digest())

        return self._thumbprint

    def __sign_request(self, payload):
        """
        Signs a payload bound for the ACME API host
        """

        payload = self._b64(json.dumps(payload).encode('utf-8'))

        protected = copy.deepcopy(self.__jws_header)
        protected['nonce'] = self.nonce
        protected = self._b64(json.dumps(protected).encode('utf-8'))

        signature = crypto.sign(self.account_key,
                                f'{protected.strip()}.{payload.strip()}')

        return json.dumps({
            'header': self.__jws_header,
            'protected': protected,
            'payload': payload,
            'signature': self._b64(signature)
        })

    def __request_challenges(self, domain):
        code, body, headers = self.__http_post(
            'new-authz',
            {
                'resource': 'new-authz',
                'identifier': {'type': 'dns', 'value': domain},
            }
        )

        if code != 201:
            raise Exception(f'Failed to request DNS challenge: {code} {body}')

        return json.loads(body.decode('utf-8'))['challenges']

    def __read_dns_challenge(self, domain, raw_challenge):
        token = re.sub(r'[^A-Za-z0-9_\-]', '_', raw_challenge['token'])

        return DNS_01_Challenge(
            raw_challenge,
            raw_challenge['status'],
            raw_challenge['token'],
            raw_challenge['uri'],
            f'_acme-challenge.{domain}.',
            self._b64(hashlib.sha256(
                f'{token}.{self.__thumbprint}'.encode('utf-8')
            ).digest())
        )

    def register(self):
        code, body, headers = self.__http_post(
            'new-reg',
            {
                'resource': 'new-reg',
                'agreement': self.endpoints['meta']['terms-of-service']
            }
        )

        if code == 201:
            return body
        elif code == 409:
            # Account key already registered.
            return
        else:
            raise Exception(
                f'Failed to register account key:\n\nStatus {code}\n\n{body}')

    def request_dns_challenge(self, domain):
        challenges = self.__request_challenges(domain)

        return self.__read_dns_challenge(domain, [c for c in challenges
                                                  if c['type'] == 'dns-01'][0])

    def refresh_challenge(self, challenge):
        """
        Returns an instance of the challenge with an updated
        status.
        """

        return challenge._replace(status=json.load(
            urllib.request.urlopen(challenge.uri))['status'])

    def validate_challenge(self, challenge):
        """
        Notify the ACME API host that the challenge is ready to be
        validated.
        """

        code, body, headers = self.__http_post(challenge.uri, {
            'resource': 'challenge',
            'keyAuthorization': f'{challenge.token}.{self.__thumbprint}',
        }, uri_mode='uri')

        if code != 202:
            raise Exception(
                f'Failed to validate challenge:\n\nStatus {code}\n\n{body}')

    def request_certificate_for_csr(self, certificate_request):
        """
        Requests a certificate for the provided Certificate Signing
        Request and returns the certificate and intermediary
        certificate.
        """

        code, body, headers = self.__http_post(
            'new-cert',
            {
                'resource': 'new-cert',
                'csr': self._b64(crypto.der_encode_csr(certificate_request))
            }
        )

        if code != 201:
            raise Exception(
                f'Failed to validate challenge:\n\nStatus {code}\n\n{body}')

        cert = os.linesep.join(
            textwrap.wrap(base64.b64encode(body).decode('utf-8'), 64)
        )

        intermediary_certificate_uri = re.match(
            r'<(.*)>;rel="up"',
            [h for h in headers
             if h[0] == 'Link' and h[1][-9:] == ';rel="up"'][0][1]
        ).group(1)

        intermediary_certificate = os.linesep.join(
            textwrap.wrap(base64.b64encode(
                urllib.request.urlopen(
                    intermediary_certificate_uri
                ).read()
            ).decode('utf-8'), 64)
        )

        return (
            f'-----BEGIN CERTIFICATE-----\n{cert}\n-----END CERTIFICATE-----',
            f'-----BEGIN CERTIFICATE-----\n{intermediary_certificate}\n-----END CERTIFICATE-----',
        )
