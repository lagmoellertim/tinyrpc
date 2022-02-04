import redis

from tinyrpc import RPCClient

redis_instance = redis.StrictRedis("localhost", 6379)

rpc = RPCClient(redis_instance)

get_index_of_array = rpc.use("get_index_of_array")
factorial = rpc.use("factorial")
test_class_instance = rpc.use("TestClass")

print(f"Variable at index 1: {get_index_of_array([123, 456, 789], 1, timeout=3)}")
print(f"Factorial of 10: {factorial(10)}")
print(f"List from 0 to 9: {test_class_instance.range_list(10)}")
print(f"Variable i of TestClass-Instance: {test_class_instance.i.val()}")
