# Configuration

Coxbuild use `Configuration` class to store configuration data. You can use `context.config` to access the configuration.

> Configuration data is a key-value pair. The key is a case-insensitive string, and the value can be any type. Coxbuild use `:` in key to split configuration sections.

```python
@beforePipeline
def initialize(context: PipelineContext):
    config = context.config
    config["a"] = 1
```

Also you can use `-c` option to specify configuration entry:

```sh
coxbuild -c a=1 -c b=2
```

Coxbuild will read configuration entries defined in environment variables (with prefix `coxbuild:`). For example `project:src` has fallback environment variable `coxbuild:project:src`.

Coxbuild will also read configuration in `coxbuild.y[a]ml` or `buildcox.json` in the current directory.
Nested dictionary will be set as sub-section.

## Project Settings

`ProjectSettings` class provide shared general configuration for projects.

```python
from coxbuild.extensions import ProjectSettings

@beforePipeline
def initialize(context: PipelineContext):
    project = ProjectSettings(context.config)
    project.src = Path("path/to/src")
```
