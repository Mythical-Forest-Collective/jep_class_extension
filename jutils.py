import functools

from java.lang import Class, String, Object, ClassLoader

from net.bytebuddy import ByteBuddy
from net.bytebuddy.matcher import ElementMatchers
from net.bytebuddy.implementation import FixedValue


system_class_loader = ClassLoader.getSystemClassLoader()

jnamed = ElementMatchers.named
jtakes_args = ElementMatchers.takesArguments
jreturns = ElementMatchers.returns


def _jmethod(jfunc_name:str, jarg_count:int):
    return getattr(jnamed(jfunc_name), "and", "and")(jtakes_args(jarg_count))

def _jmethod_rt(jfunc_name:str, jreturn_type:type(Class), jarg_count:int):
    return getattr(getattr(jnamed(jfunc_name), "and")(jreturns(jreturn_type)), "and")(jtakes_args(jarg_count))


def _finalise(cls):
    for attr in dir(cls):
        if hasattr(getattr(cls, attr), "_jmethod_name"):
            print(attr)
            jmethod_name = getattr(cls, attr)._jmethod_name
            jarg_count = getattr(cls, attr)._jarg_count
            jreturn_type_exists = hasattr(getattr(cls, attr), "_jreturn_type")

            if jreturn_type_exists:
                cls._bytebuddy = cls._bytebuddy.method(_jmethod_rt(jmethod_name, jreturn_type, jarg_count)).intercept(FixedValue(getattr(cls, attr)))
            else:
                cls._bytebuddy = cls._bytebuddy.method(_jmethod(jmethod_name, jarg_count)).intercept(FixedValue(getattr(cls, attr)))

    cls._bytebuddy = cls._bytebuddy.make().load(system_class_loader).getLoaded()


def JExtend(jclass, cls=None):
    if cls is None:
        return functools.partial(JExtend, jclass)
    
    setattr(cls, "_bytebuddy", ByteBuddy().subclass(jclass))
    setattr(cls, "finalise", functools.partial(_finalise, cls))
    setattr(cls, "finalize", functools.partial(_finalise, cls))
    return cls

def JMethod(jmethod_name, jarg_count, jreturn_type=None):
    def wrapper(func):
        setattr(func, "_jmethod_name", jmethod_name)
        setattr(func, "_jarg_count", jarg_count)

        if jreturn_type:
            setattr(func, "_jreturn_type", jreturn_type)

        return func
    return wrapper

'''
bb = ByteBuddy()                                       \
    .subclass(Object)                                  \
    .method(_jmethod("toString", String, 0))           \
    .intercept(FixedValue.value("Hiya Cursed World"))  \
    .make()                                            \
    .load(system_class_loader)                         \
    .getLoaded()

print(bb())
'''