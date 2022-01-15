from coxbuild import schema
from coxbuild.schema import group

task = group("")


@task()
def list():
    """List all defined tasks."""
    for item in schema.pipeline.tasks.values():
        print(f"📜 {item.name} 🔰 {item.doc}")


@task()
def serve():
    """Start event-based service."""
    schema.service()
