import coxbuild
from coxbuild import schema
from coxbuild.configuration import Configuration
from coxbuild.tasks import depend, group, task


@group("")
@task
def list():
    """List all defined tasks."""
    for item in schema.pipeline.tasks.values():
        print(f"📜 {item.name}")
        if item.doc:
            print(f"  #️⃣  {item.doc}")
        if item.deps:
            print(f"  *️⃣  {', '.join(item.deps)}")


@group("")
@task
async def serve():
    """Start event-based service."""
    await schema.service()


@task
async def default():
    """Default task when no user-defined default task."""
    if len(schema.service.handlers) > 0:
        await serve()
    else:
        await list()
