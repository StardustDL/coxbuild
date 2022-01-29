from coxbuild.schema import ext
from coxbuild.tasks import depend, task

mod = ext("url://https://raw.githubusercontent.com/StardustDL/coxbuild/master/demo/event.py").module


@mod.attime_do.handler.after
def after_attime_do(*args, **kwds):
    print("after extension module attime_do event")
