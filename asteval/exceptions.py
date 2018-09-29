

class EvalError(Exception):
    def __init__(self, error=None, traceback="", cause=None, *args):
        self.error = error
        self.traceback = traceback
        self.cause = cause
        self.args = (self.error, self.traceback, self.cause) + args
    
    def extend_traceback(self, tb_msg):
        return self.__class__(self.error, tb_msg + '\n' + self.traceback, *self.args[2:])
        

class UserError(EvalError):
    pass

class RaisedError(UserError):
    pass

class BuiltinError(UserError):
    pass

class OperatorError(BuiltinError):
    pass

class TimeOutError(EvalError):
    pass
