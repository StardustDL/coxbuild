from coxbuild.schema import (Configuration, continueOnError, depend, task,
                             withConfiguration)


@continueOnError
@task
def error(): assert False


@withConfiguration
@depend(error)
@task
def default(config: Configuration):
    print(f"Hello, {config.get('name')}, {config.get('id')}!")
