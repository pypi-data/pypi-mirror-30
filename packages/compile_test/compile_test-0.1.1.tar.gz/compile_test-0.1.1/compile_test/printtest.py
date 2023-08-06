import os
import inspect
import traceback
filepath = "InterfaceGenerator.py"
source = open(filepath).read()
co = compile(source,filepath,"exec")

module = __import__(filepath[:-3])
for n in module.__dict__:
    if type(module.__dict__[n]) == type(object) and not n.startswith("__"):
        print n
        cls = getattr(module,n)
        print  issubclass(cls,list)
        for fname in cls.__dict__:

            if not fname.startswith("__"):
                print fname
                func = cls.__dict__[fname]
                print inspect.getargspec(func)
