from coxbuild import schema
import coxbuild
from coxbuild.schema import group, config
from coxbuild.configuration import Configuration


task = group("")


@task()
def list():
    """List all defined tasks."""
    for item in schema.pipeline.tasks.values():
        print(f"📜 {item.name} 🔰 {item.doc}")


@task()
async def serve():
    """Start event-based service."""
    await schema.service()
