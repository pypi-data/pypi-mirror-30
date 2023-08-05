#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import binascii
import hashlib
import json
import re
import urllib.request
import urllib.error
from triplecask import crypto
from triplecask.acme_v02.types import DNS_01_Challenge, Order

STAGING_DIRECTORY_URI = 'https://acme-staging-v02.api.letsencrypt.org/directory'
PRODUCTION_DIRECTORY_URI = 'https://acme-v02.api.letsencrypt.org/directory'


class ACME(object):

    _b64 = lambda _, x: base64.urlsafe_b64encode(x).decode('utf-8').rstrip('=')

    def __init__(self, account_key, directory_uri=STAGING_DIRECTORY_URI):
        """
        Creates a new ACME client instance for a given private key.
        """

        self.account_key = account_key

        r = urllib.request.urlopen(directory_uri)

        self.endpoints = json.load(r)
        self.nonce = urllib.request.urlopen(
            self.endpoints['newNonce']).getheader('Replay-Nonce', None)
        self.kid = None
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
            resp = urllib.request.urlopen(urllib.request.Request(
                uri, data=self.__sign_request(uri, payload).encode('utf-8'),
                headers={'Content-Type': 'application/jose+json'}))
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

    def __sign_request(self, uri, payload):
        """
        Signs a payload bound for the ACME API host
        """

        payload = self._b64(json.dumps(payload).encode('utf-8'))

        protected = {}
        protected['alg'] = self.__jws_header['alg']
        protected['nonce'] = self.nonce
        protected['url'] = uri

        if self.kid is None:
            protected['jwk'] = self.__jws_header['jwk']
        else:
            protected['kid'] = self.kid

        protected = self._b64(json.dumps(protected).encode('utf-8'))

        signature = crypto.sign(self.account_key,
                                f'{protected.strip()}.{payload.strip()}')

        return json.dumps({
            'protected': protected,
            'payload': payload,
            'signature': self._b64(signature)
        })

    def __read_dns_challenge(self, challenge_uri):
        raw_challenge = json.load(urllib.request.urlopen(challenge_uri))

        dns_challenge = [c for c in raw_challenge['challenges']
                         if c['type'] == 'dns-01'][0]

        token = re.sub(r'[^A-Za-z0-9_\-]', '_', dns_challenge['token'])
        domain = raw_challenge['identifier']['value']

        return DNS_01_Challenge(
            raw_challenge,
            raw_challenge['status'],
            dns_challenge['token'],
            challenge_uri,
            dns_challenge['url'],
            f'_acme-challenge.{domain}.',
            '"{}"'.format(self._b64(hashlib.sha256(
                f'{token}.{self.__thumbprint}'.encode('utf-8')
            ).digest()))
        )

    def __read_order(self, raw, domains, refresh_uri):
        return Order(
            raw,
            raw['status'],
            domains,
            raw['expires'],
            [self.__read_dns_challenge(a) for a in raw['authorizations']],
            raw.get('certificate', None),
            refresh_uri,
            raw['finalize']
        )

    def register(self):
        code, body, headers = self.__http_post(
            'newAccount',
            {
                'termsOfServiceAgreed': True
            }
        )

        if code == 200 or code == 201:
            self.kid = [h[1] for h in headers if h[0] == 'Location'][0]
        if code == 201:
            return body
        elif code == 200:
            # Account key already registered.
            return
        else:
            raise Exception(
                f'Failed to register account key:\n\nStatus {code}\n\n{body}')

    def new_order(self, domains):
        code, body, headers = self.__http_post(
            'newOrder',
            {
                'identifiers': [{'type': 'dns', 'value': domain}
                                for domain in domains],
            }
        )

        if code != 201:
            raise Exception(f'Failed to submit order: {code} {body}')

        resp = json.loads(body.decode('utf-8'))

        return self.__read_order(
            resp,
            domains,
            [h[1] for h in headers if h[0] == 'Location'][0]
        )

    def refresh_order(self, order):
        """
        Returns an updated instance of the order
        """

        raw = json.loads(urllib.request.urlopen(order.refresh_uri).read().decode('utf-8'))
        return self.__read_order(raw, order.domains, order.refresh_uri)

    def finalize_order(self, order, certificate_signing_request):
        code, body, headers = self.__http_post(
            order.finalize_uri,
            {'csr': self._b64(crypto.der_encode_csr(certificate_signing_request))},
            uri_mode='uri'
        )

        if code == 200:
            return self.__read_order(
                json.loads(body.decode('utf-8')), order.domains, order.refresh_uri
            )

        else:
            raise Exception(f'Failed to finalize order: {code} {body}')

    def certificate_chain_for_order(self, order):
        if order.certificate_uri is None:
            return

        return urllib.request.urlopen(order.certificate_uri).read().decode('utf-8')

    def refresh_challenge(self, challenge):
        """
        Returns an instance of the challenge with an updated
        status.
        """

        return self.__read_dns_challenge(challenge.refresh_uri)

    def validate_challenge(self, challenge):
        """
        Notify the ACME API host that the challenge is ready to be
        validated.
        """

        code, body, headers = self.__http_post(
            challenge.finalize_uri,
            {},
            uri_mode='uri'
        )

        if code != 200:
            raise Exception(
                f'Failed to validate challenge:\n\nStatus {code}\n\n{body}')
