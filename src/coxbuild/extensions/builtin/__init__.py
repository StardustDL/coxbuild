import coxbuild
from coxbuild.configuration import Configuration
from coxbuild.pipelines import Pipeline
from coxbuild.services import Service
from coxbuild.tasks import depend, group, task
from coxbuild.runtime import withManager, withPipeline, withService
from coxbuild.managers import Manager

grouped = group("")


@grouped
@withPipeline
@task
def list(*, pipeline: Pipeline):
    """List all defined tasks."""
    for item in pipeline.tasks.values():
        print(f"📜 {item.name}")
        if item.description:
            print(f"  #️⃣  {item.description}")
        if item.deps:
            print(f"  *️⃣  {', '.join(item.deps)}")


@grouped
@withManager
@task
def ext(*, manager: "Manager"):
    """List all defined tasks."""
    for item in manager.extensions.values():
        print(f"📜 {item.name} ({item.uri})")
        if item.description:
            print(f"  #️⃣  {item.description}")
        if item.version:
            print(f"  *️⃣  {item.version}")


@grouped
@withService
@task
async def serve(*, service: Service):
    """Start event-based service."""
    await service()


@withService
@withPipeline
@task
async def default(*, pipeline: Pipeline, service: Service):
    """Default task when no user-defined default task."""
    if len(service.handlers) > 0:
        await serve(service=service)
    else:
        await list(pipeline=pipeline)
