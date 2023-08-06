from functools import wraps,update_wrapper

def log(func):

    @wraps(func)
    def wrap(*args,**kwargs):
        print args
        print kwargs
        return func(*args,**kwargs)
    return wrap

class LoggerMeta(type):
    def __new__(cls, name,base,properties):
        wrap_p = {}
        for key, value in properties.items():
            value = log(value)

            wrap_p[key] = value

        # wrap_p = {key:log(value) for key,value in properties.items() if not key.startswith("__")}
        # print wrap_p
        properties.update(**wrap_p)
        return type.__new__(cls,name,base,properties)


class Test2(object):

    def test_func(a,b):
        return a,b

class Test(object):
    #__metaclass__ = LoggerMeta

    @staticmethod
    def test_func(a,b):
        return a,b

if __name__ == '__main__':
    # import inspect
    # print Test.test_func
    #
    # Test.test_func(1,2)
    print Test.test_func.func_name