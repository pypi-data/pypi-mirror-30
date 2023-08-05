import uuid


class Method:
    def __init__(self, name, request):
        self._name = name
        self._request = request

    def __call__(self, *args):
        self._params = args
        return self._request(self._serialize())

    def _serialize(self):
        return {
            "id": uuid.uuid4().__str__(),
            "method": self._name,
            "params": self._params
        }
