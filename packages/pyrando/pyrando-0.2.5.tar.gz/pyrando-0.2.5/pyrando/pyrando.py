#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This is a module for sending requests to the Random.ORG API
and returns the response as an ordered dict.
"""

import json
import uuid
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

    def usage(self):
        method = 'getUsage'
        params = {'apiKey': self.api_key}

        request = self.generate_request(method, params)
        response = self.api_response(request)
        return response

    @staticmethod
    def generate_request(method, params):
        return {'jsonrpc': '2.0', 'method': method, 'params': params, 'id': uuid.uuid4().hex}

    @staticmethod
    def api_response(payload):
        response = requests.post(
            'https://api.random.org/json-rpc/1/invoke', data=json.dumps(payload),
            headers={'content-type': 'application/json'}).json(object_pairs_hook=OrderedDict)

        return response


if __name__ == '__main__':
    import os

    api_key = os.environ.get('RO_API_KEY')

    pr = PyRando(api_key)

