import functools

from coxbuild.schema import *
from coxbuild.tasks import TaskResult


def log(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        print(f"Lifecycle: {f.__name__}")
        return f(*args, **kwds)

    return wrapper


@log
def precond_task1(*args, **kwds):
    return True


@log
def precond_task2(*args, **kwds):
    return True


@log
def postcond_task1(*args, **kwds):
    return True


@log
def postcond_task2(*args, **kwds):
    return True


@log
def before_task1(context: TaskContext):
    context.args.extend([1, 2, 3])
    context.kwds.update(a=1, b=2)
    print(context.config)
    # return False to ignore this task


@log
def after_task1(context: TaskContext, result: TaskResult):
    pass


@log
def setup_task1(*args, **kwds):
    pass


@log
def teardown_task1(*args, **kwds):
    pass


@teardown(teardown_task1)
@setup(setup_task1)
@after(after_task1)
@before(before_task1)
@precond(precond_task1)
@postcond(postcond_task1)
@task
@log
def task1(*args, **kwds):
    print(f"task1: {args}, {kwds}")


@precond(precond_task2)
@postcond(postcond_task2)
@task
@log
def task2(*args, **kwds):
    print(f"task2: {args}, {kwds}")


@beforeTask
@log
def pipeline_before(context: TaskContext):
    if context.task.name != "default":
        context.args.extend(["a", "b", "c"])
        context.kwds.update(p="p")
    # return False to ignore this task


@task2.before
@log
def before_task2(context: TaskContext):
    context.args.extend([4, 5, 6])
    context.kwds.update(x=1, y=2)
    return True  # return False to ignore this task


@afterTask
@log
def pipeline_after(context: TaskContext, result: TaskResult):
    pass


@task2.after
@log
def after_task2(context: TaskContext, result: TaskResult):
    pass


@task2.setup
@log
def setup_task2(*args, **kwds):
    pass


@task2.teardown
@log
def teardown_task2(*args, **kwds):
    pass


@beforePipeline
@log
def before_pipeline(context: PipelineContext):
    return True  # return False to cancel pipeline


@afterPipeline
@log
def after_pipeline(context: PipelineContext, result: PipelineResult):
    pass


@depend(task1, task2)
@task
def default():
    pass
