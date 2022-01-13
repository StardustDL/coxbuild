from coxbuild.schema import depend, run, grouptask

task = grouptask("python")


@task
def prebuildPackage():
    run(["python", "-m", "pip", "install", "--upgrade", "build", "twine"], retry=3)


@task
def buildPackage():
    run(["python", "-m", "build"])


@task
def deployPackage():
    run(["python", "-m", "twine", "upload",
        "--skip-existing", "--repository", "pypi", "dist/*"])
