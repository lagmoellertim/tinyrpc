import threading
from datetime import datetime

import redis

from tinyrpc.serializer import JSONSerializer


class RPCServer(threading.Thread):
    def __init__(self, redis_client: redis.Redis, serializer=JSONSerializer):
        super().__init__()
        self.__redis = redis_client
        self.__serializer = serializer
        self.__server_list = []

    def register(self, rpc_name, obj):
        self.__server_list.append(
            RPCObjectServer(self.__redis, rpc_name, obj, serializer=self.__serializer)
        )

    def fn(self, func):
        self.register(func.__name__, func)
        return func

    def run(self):
        for server in self.__server_list:
            server.start()


class RPCObjectServer(threading.Thread):
    def __init__(self, redis_client: redis.Redis, rpc_name, obj, serializer=JSONSerializer, task_timeout=2,
                 loop_delay=0.5):
        super().__init__()
        self.__redis = redis_client
        self.__rpc_name = rpc_name
        self.__object = obj
        self.__serializer = serializer
        self.__task_timeout = task_timeout
        self.__loop_delay = loop_delay
        self.__running = False

    def run(self):
        self.__running = True

        while self.__running:
            redis_response = self.__redis.blpop(self.__rpc_name, timeout=self.__loop_delay)

            if redis_response is None:
                continue

            serialized_call_descriptor = redis_response[1]

            call_descriptor = self.__serializer.deserialize(serialized_call_descriptor)

            second_difference = (
                    datetime.utcnow() - datetime.fromtimestamp(call_descriptor["timestamp"])
            ).total_seconds()

            if second_difference >= self.__task_timeout:
                continue

            try:
                if call_descriptor["call_type"] == "variable":
                    result = getattr(self.__object, call_descriptor["variable"])
                elif call_descriptor["call_type"] == "function":
                    result = self.__object(
                        *call_descriptor["args"],
                        **call_descriptor["kwargs"]
                    )
                elif call_descriptor["call_type"] == "object":
                    result = getattr(self.__object, call_descriptor["method"])(
                        *call_descriptor["args"],
                        **call_descriptor["kwargs"]
                    )
                else:
                    raise NotImplementedError("Invalid Call Type")

                response = {"ok": True, "result": result}

            except Exception as e:
                response = {"ok": False, "exception": repr(e)}

            serialized_response = self.__serializer.serialize(response)
            self.__redis.rpush(call_descriptor["request_id"], serialized_response)

    def stop(self):
        self.__running = False
