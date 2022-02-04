import redis

from tinyrpc import RPCServer

redis_instance = redis.StrictRedis("localhost", 6379)

rpc = RPCServer(redis_instance)


@rpc.fn
def get_index_of_array(array, index):
    return array[index]


@rpc.fn
def factorial(n):
    if n == 0:
        return 1

    return factorial(n - 1) * n


class TestClass:
    def range_list(self, n):
        return list(range(n))

    i = 10


rpc.register("TestClass", TestClass())

if __name__ == "__main__":
    rpc.start()
