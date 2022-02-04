import uuid
from datetime import datetime

import redis

from tinyrpc.exception import RPCTimeoutException, RPCFunctionException
from tinyrpc.serializer import JSONSerializer


class RPCClient:
    def __init__(self, redis_client: redis.Redis, serializer=JSONSerializer):
        self.__redis = redis_client
        self.__serializer = serializer

    def use(self, rpc_name):
        return RPCObjectClient(self.__redis, rpc_name, self.__serializer)


class RPCObjectClient:
    def __init__(self, redis_client: redis.Redis, rpc_name, serializer=JSONSerializer):
        self.__redis = redis_client
        self.__rpc_name = rpc_name
        self.__serializer = serializer

    def execute_call(self, member_name="", args=None, kwargs=None, timeout=10, call_type="function"):
        request_id = str(uuid.uuid4())

        call_descriptor = {
            "request_id": request_id,
            "call_type": call_type,
            "timestamp": datetime.utcnow().timestamp()
        }

        if call_type == "function" or call_type == "object":
            call_descriptor["args"] = [] if args is None else args
            call_descriptor["kwargs"] = {} if kwargs is None else kwargs

            if call_type == "object":
                call_descriptor["method"] = member_name

        elif call_type == "variable":
            call_descriptor["variable"] = member_name

        else:
            raise NotImplementedError()

        serialized_call_descriptor = self.__serializer.serialize(call_descriptor)

        self.__redis.rpush(self.__rpc_name, serialized_call_descriptor)

        redis_response = self.__redis.brpop(request_id, timeout=timeout)

        if redis_response is None:
            raise RPCTimeoutException()

        serialized_response = redis_response[1]
        response = self.__serializer.deserialize(serialized_response)

        if response["ok"]:
            return response["result"]

        raise RPCFunctionException(response["exception"])

    def __call__(self, *args, timeout=10, **kwargs):
        return self.execute_call(args=args, kwargs=kwargs, timeout=timeout, call_type="function")

    def __getattr__(self, member_name):
        return ReturnValue(self, member_name)


class ReturnValue:
    def __init__(self, client_instance: RPCObjectClient, member_name):
        self.__client_instance = client_instance
        self.__member_name = member_name

    def __call__(self, *args, timeout=10, **kwargs):
        return self.__client_instance.execute_call(
            member_name=self.__member_name,
            args=args,
            kwargs=kwargs,
            timeout=timeout,
            call_type="object"
        )

    def val(self, timeout=10):
        return self.__client_instance.execute_call(
            member_name=self.__member_name,
            timeout=timeout,
            call_type="variable"
        )
