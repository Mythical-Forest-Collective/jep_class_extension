import sys

sys.path.append('.')

from jutils import *

from java.lang import Object, String


@JExtend(Object)
class Test:
    @JMethod("object", Object, 0)
    def constructor(self):
        return self

    @JMethod("toString", String, 0)
    def to_string(self):
        return "Hiya Cursed World"


Test.finalise()
