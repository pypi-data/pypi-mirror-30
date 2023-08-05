# -*- coding:utf-8 -*-

import BaseHTTPServer
import json
import socket
import logging

class CNrpcServer:
    def __init__(self, net_interface):
        assert isinstance(net_interface, tuple)

        self._host, self.port = net_interface
        self._funcs = {}

    def register_function(self, func, name=None):
        assert callable(func)

        if name is None:
            name = func.func_name
        self._funcs[name] = func

    def serve_forever(self):
        s = socket.socket()
        s.bind((self._host, self.port))
        s.listen(5)

        while True:
            client, addr = s.accept()
            msg = client.recv(1024)
            request = json.loads(msg, encoding="utf-8")
            response = self._call_function(request["id"], request["method"], request["params"])
            str_response = json.dumps(response, encoding="utf-8")
            client.send(str_response)
            client.close()

    def _call_function(self, id, name, params):
        msg = dict(id=id)
        func = self._funcs.get(name)
        if func is None:
            msg["flag"] = False
            msg["result"] = "No function named '{}' has been registered".format(name)

        else:
            try:
                msg["flag"] = True
                msg["result"] = func(*params)
            except Exception as e:
                msg["flag"] = False
                msg["result"] = e.message

        print msg
        return msg


if __name__ == '__main__':
    server = CNrpcServer(("localhost", 7070))

    def add(a,b): return a+b

    server.register_function(add)

    server.serve_forever()