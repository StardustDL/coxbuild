# How It Works

Coxbuild works as a framework to run tasks.

## Workflow

1. Create runtime environment (pipelines, services, configuration, and managers in `schema` module).
2. Load builtin extensions (the `coxbuild.extensions.builtin` module).
3. Read schema in schema file (default: `buildcox.py`) and load it as a module, then load it as an extension.
4. Execute the pipeline with the specified tasks.

## Extension Loading

A extension is just a Python module, which contains some tasks, event handlers, and hooks.

The manager will traverse the extension module (no recursion) and register all the tasks, event handlers, and hooks.

> The member name with `_` prefix will be ignored.
