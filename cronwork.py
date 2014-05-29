#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

import requests

from addons.mongo2s import mongod

data = json.dumps(dict(
        xh = '1111051046',
        pw = 'zhejiushimima'))

headers={'accesstoken':'203ccbb1c5d05d2a58bf6d81e68fb9b2'}

url="http://api.t.gotit.asia/score/current_semester.json?nocode=true"

req = requests.post(url, data=data, headers=headers)

print req.content
