import coxbuild
from coxbuild import schema
from coxbuild.configuration import Configuration
from coxbuild.schema import config, group

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
