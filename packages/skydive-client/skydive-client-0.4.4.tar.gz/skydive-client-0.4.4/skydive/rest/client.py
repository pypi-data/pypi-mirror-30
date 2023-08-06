#
# Copyright (C) 2017 Red Hat, Inc.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import json
import ssl
try:
    import urllib.request as request
except ImportError:
    import urllib2 as request

from skydive.auth import Authenticate
from skydive.graph import Node, Edge


class RESTClient:
    def __init__(self, endpoint, scheme="http",
                 username="", password="",
                 insecure=False, debug=0):
        self.endpoint = endpoint
        self.scheme = scheme
        self.username = username
        self.password = password
        self.insecure = insecure
        self.debug = debug

        self.auth = Authenticate(endpoint, scheme,
                                 username, password, insecure)

    def request(self, path, data=None):
        if self.username and not self.auth.authenticated:
            self.auth.login()

        handlers = []
        url = "%s://%s%s" % (self.scheme, self.endpoint, path)
        handlers.append(request.HTTPHandler(debuglevel=self.debug))
        handlers.append(request.HTTPCookieProcessor(self.auth.cookie_jar))

        if self.scheme == "https":
            if self.insecure:
                context = ssl._create_unverified_context()
            else:
                context = ssl._create_default_context()
            handlers.append(request.HTTPSHandler(debuglevel=self.debug,
                                                 context=context))

        opener = request.build_opener(*handlers)

        headers = {'Content-Type': 'application/json'}
        req = request.Request(url, data=data, headers=headers)

        try:
            resp = opener.open(req)
        except request.HTTPError as err:
            self.auth.logout()
            raise

        return resp

    def lookup(self, gremlin, klass=None):
        data = json.dumps(
            {"GremlinQuery": gremlin}
        )

        resp = self.request("/api/topology", data.encode())

        data = resp.read()
        objs = json.loads(data.decode())
        if klass:
            return [klass.from_object(o) for o in objs]
        return objs

    def lookup_nodes(self, gremlin):
        return self.lookup(gremlin, Node)

    def lookup_edges(self, gremlin):
        return self.lookup(gremlin, Edge)
