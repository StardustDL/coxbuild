from coxbuild.schema import Configuration, task, withConfiguration


@withConfiguration
@task
def default(config: Configuration):
    print(f"Hello, {config.get('name')}, {config.get('id')}!")
