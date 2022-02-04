class RPCException(Exception):
    pass


class RPCTimeoutException(RPCException):
    pass


class RPCFunctionException(RPCException):
    pass
