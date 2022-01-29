@task
def initial():
    print("Initializing...")


@depend(initial)
@task
def default():
    print("Hello, world!")
