# How It Works

Coxbuild works as a framework to run tasks.

## Workflow

1. Create runtime environment (pipelines, services, configuration, and managers in `schema` module).
2. Load builtin extensions (the `coxbuild.extensions.builtin` module).
3. Read schema in schema file (default: `buildcox.py`) and load it as a module, then load it as an extension.
4. Execute the pipeline with the specified tasks.
