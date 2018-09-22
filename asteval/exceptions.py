

class EvalError(Exception):
    pass

class UserError(EvalError):
    
    def get_error(self):
        if len(self.args):
            return self.args[0]
        else:
            return None

class RaisedError(UserError):
    pass

class BuiltinError(UserError):
    pass

class TimeOutError(EvalError):
    pass
