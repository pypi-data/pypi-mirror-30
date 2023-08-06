#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

class Connection:

    def __init__(self):
        print "CONNECTION INIT"

    def load(self):
        url = 'http://localhost:9500/console/service'
        params = dict(
            id="507f191e810c19729de860ea"
        )

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'devdoo-api-key': '286c42a2b9dabb536c87b1a88a6842117bfb37ab',
            'devdoo-app-id': '507f191e810c19729de860ea',
            'devdoo-credentials': 'NTA3ZjE5MWU4MTBjMTk3MjlkZTg2MGVhOjhmNGY5ZjJkY2JhZjliZDhlZTllNGQxYTJjYjk3MWEwNDA4NDE1N2I='
        }
        response = requests.get(url, params=params, headers=headers)


        print "response-status_code", response.status_code, response.encoding
        print "response.json()", response.json()

        return response.json()