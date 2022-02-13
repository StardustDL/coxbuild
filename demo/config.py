from coxbuild.schema import (Configuration, continueOnError, depend, task,
                             withConfig)


@continueOnError
@task
def error(): assert False


@withConfig
@depend(error)
@task
def default(config: Configuration):
    print(f"Hello, {config.get('name')}, {config.get('id')}!")
