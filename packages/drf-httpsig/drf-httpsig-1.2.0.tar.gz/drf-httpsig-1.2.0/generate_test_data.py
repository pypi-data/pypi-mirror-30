#!/usr/bin/env python3

from httpsig import HeaderSigner

ENDPOINT = '/api'
METHOD = 'GET'
KEYID = 'some-key'
SECRET = 'my secret string'
SIGNATURE = 'some.signature'

headers = ['(request-target)', 'accept', 'date', 'host']
hs = HeaderSigner(KEYID, SECRET, "hmac-sha256", headers)

unsigned = {
    'Host': 'localhost:8000',
    'Date': 'Mon, 17 Feb 2014 06:11:05 GMT',
    'Accept': 'application/json',
}
signed = hs.sign(unsigned, method="GET", path='/packages/measures/')
print(signed)
