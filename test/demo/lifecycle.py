from coxbuild.schema import *
import functools


def log(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        print(f"Lifecycle: {f.__name__}")
        f(*args, **kwds)

    return wrapper


@task()
@log
def task1(*args, **kwds):
    print(f"task1: {args}, {kwds}")


@task()
@log
def task2(*args, **kwds):
    print(f"task2: {args}, {kwds}")


@before()
@log
def pipeline_before(context: TaskContext):
    if context.task.name != "default":
        context.args.extend(["a", "b", "c"])
        context.kwds.update(p="p")
    # return False to ignore this task


@before(task1)
@log
def before_task1(context: TaskContext):
    context.args.extend([1, 2, 3])
    context.kwds.update(a=1, b=2)
    # return False to ignore this task


@before(task2)
@log
def before_task2(context: TaskContext):
    context.args.extend([4, 5, 6])
    context.kwds.update(x=1, y=2)
    return True  # return False to ignore this task


@after()
@log
def pipeline_after(context: TaskContext, result: TaskResult):
    pass


@after(task1)
@log
def after_task1(context: TaskContext, result: TaskResult):
    pass


@after(task2)
@log
def after_task2(context: TaskContext, result: TaskResult):
    pass


@setup(task1)
@log
def setup_task1(*args, **kwds):
    pass


@setup(task2)
@log
def setup_task2(*args, **kwds):
    pass


@teardown(task1)
@log
def teardown_task1(*args, **kwds):
    pass


@teardown(task2)
@log
def teardown_task2(*args, **kwds):
    pass


@setup()
@log
def setup_pipeline(context: PipelineContext):
    return True  # return False to cancel pipeline


@teardown()
@log
def teardown_pipeline(context: PipelineContext, result: PipelineResult):
    pass


@depend(task1, task2)
@task()
def default():
    pass
