# -*- coding:utf-8 -*-
import socket
import json
from method import Method


class CNrpcClient:
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def __getattr__(self, name):
        return Method(name, self._request)

    def _request(self, serialize_method):
        s = socket.socket()
        s.connect((self._host, self._port))
        s.send(json.dumps(serialize_method))
        res = s.recv(1024)
        s.close()

        res = json.loads(res, encoding="utf-8")

        assert res["id"] == serialize_method["id"]

        if res["flag"]:
            return res["result"]
        else:
            raise RuntimeError(res["result"])


if __name__ == '__main__':
    client = CNrpcClient("localhost", 7070)
    print client.add(1, 2)
    print client.add2(1, 2)

