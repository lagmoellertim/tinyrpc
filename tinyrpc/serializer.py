import json
import pickle


class JSONSerializer:
    @staticmethod
    def serialize(obj: dict):
        return json.dumps(obj)

    @staticmethod
    def deserialize(s: str):
        return json.loads(s)


class PickleSerializer:
    @staticmethod
    def serialize(obj: dict):
        return pickle.dumps(obj)

    @staticmethod
    def deserialize(b: bytes):
        return pickle.loads(b)
