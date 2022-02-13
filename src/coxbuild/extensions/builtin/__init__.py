import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.extensions import ProjectSettings, withProject
from coxbuild.managers import Manager
from coxbuild.pipelines import Pipeline
from coxbuild.runtime import (ExecutionState, withExecutionState, withManager,
                              withPipeline, withService)
from coxbuild.services import Service
from coxbuild.tasks import depend, group, task

grouped = group("")


@grouped
@withPipeline
@task
def list(*, pipeline: Pipeline):
    """List all defined tasks."""
    for item in pipeline.tasks.values():
        print(f"📜  {item.name}")
        if item.description:
            print(f"  📖  {item.description}")
        if item.deps:
            print(f"  🔗  {', '.join([t.name for t in item.deps])}")
        if item.extension:
            print(f"  ⚓  {item.extension.uri}")


@grouped
@withProject
@task
def project(*, project: ProjectSettings):
    print(f"Name        : {project.name}")
    print(f"Description : {project.description}")
    print(f"Version     : {project.version}")
    print(f"Author      : {project.author}")
    print(f"Source Code : {project.src}")
    print(f"Test        : {project.test}")
    print(f"Document    : {project.docs}")
    print(f"Package     : {project.package}")


@grouped
@withManager
@task
def ext(*, manager: "Manager"):
    """List all registered extensions."""
    for item in manager.extensions.values():
        print(f"⚓  {item.name}")
        if item.uri:
            print(f"  🔗  {item.uri}")
        if item.description:
            print(f"  📖  {item.description}")
        if item.version:
            print(f"  📌  {item.version}")
        if item.hashcode:
            print(f"  🔑  {item.hashcode}")


@grouped
@withService
@task
async def serve(*, service: Service):
    """Start event-based service."""
    await service()
