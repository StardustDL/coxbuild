# How It Works

Coxbuild works as a framework to run tasks.

## Workflow

1. Create runtime environment (managers in `schema` module).
2. Load builtin extensions (the `coxbuild.extensions.builtin` module).
3. Read schema by extension URI (default: `file://buildcox.py`) and load it as a module.
4. Load all extensions and prepare runtime environment, such as configuration.
5. Execute the pipeline with the specified tasks.
