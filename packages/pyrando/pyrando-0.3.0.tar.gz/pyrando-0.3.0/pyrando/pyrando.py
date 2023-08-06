#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a module for sending requests to the Random.ORG API
and returns the response as an ordered dict.
"""

import json
import secrets
from collections import OrderedDict

import requests


class PyRando(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def integers(self, n, min, max, base=10):
        method = 'generateIntegers'
        params = {'apiKey': self.api_key, 'n': n, 'min': min,
                  'max': max, 'base': base}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def decimals(self, n, dec_places):
        method = 'generateDecimalFractions'
        params = {'apiKey': self.api_key, 'n': n, 'decimalPlaces': dec_places}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def gaussians(self, n, mean, std_dev, sig_digits):
        method = 'generateGaussians'
        params = {'apiKey': self.api_key, 'n': n, 'mean': mean,
                  'standardDeviation': std_dev, 'significantDigits': sig_digits}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def uuids(self, n):
        method = 'generateUUIDs'
        params = {'apiKey': self.api_key, 'n': n}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def strings(self, n, length, characters):
        method = 'generateStrings'
        params = {'apiKey': self.api_key, 'n': n, 'length': length, 'characters': characters}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def blobs(self, n, size, format='base64'):
        method = 'generateBlobs'
        params = {'apiKey': self.api_key, 'n': n, 'size': size,
                  'format': format}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response['result']['random']['data']

    def signed_integers(self, n, min, max, base=10):
        method = 'generateSignedIntegers'
        params = {'apiKey': self.api_key, 'n': n, 'min': min,
                  'max': max, 'base': base}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def signed_decimals(self, n, dec_places):
        method = 'generateSignedDecimalFractions'
        params = {'apiKey': self.api_key, 'n': n, 'decimalPlaces': dec_places}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def signed_gaussians(self, n, mean, std_dev, sig_digits):
        method = 'generateSignedGaussians'
        params = {'apiKey': self.api_key, 'n': n, 'mean': mean,
                  'standardDeviation': std_dev, 'significantDigits': sig_digits}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def signed_uuids(self, n):
        method = 'generateSignedUUIDs'
        params = {'apiKey': self.api_key, 'n': n}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def signed_strings(self, n, length, characters):
        method = 'generateSignedStrings'
        params = {'apiKey': self.api_key, 'n': n, 'length': length, 'characters': characters}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def signed_blobs(self, n, size, format='base64'):
        method = 'generateSignedBlobs'
        params = {'apiKey': self.api_key, 'n': n, 'size': size,
                  'format': format}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return self.signed_response(response)

    def verify_signature(self, random, signature):
        method = 'verifySignature'
        params = {'random': random, 'signature': signature}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return bool(response['result']['authenticity'])

    def usage(self):
        method = 'getUsage'
        params = {'apiKey': self.api_key}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response

    @staticmethod
    def generate_request(method, params):
        return {'jsonrpc': '2.0', 'method': method, 'params': params, 'id': secrets.token_hex(16)}

    @staticmethod
    def api_response(payload):
        response = requests.post(
            'https://api.random.org/json-rpc/1/invoke', data=json.dumps(payload),
            headers={'content-type': 'application/json'}).json(object_pairs_hook=OrderedDict)
        return response

    @staticmethod
    def signed_response(response):
        return {'data': response['result']['random']['data'],
                'random': response['result']['random'],
                'signature': response['result']['signature']}
