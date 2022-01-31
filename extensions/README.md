# Extensions

An extension is a wrapped Python module, which contains some tasks, event handlers, and hooks.

Use `ext` function to register extension by a loaded module or an extension URI. It will load and register the extension and then return it.

When executing, the manager will traverse the extension module (no recursion) and register all the tasks, event handlers, and hooks.

> The member name with `_` prefix will be ignored, so we recomment to use `_` prefix for tasks, event handlers, and hooks imported from other extension.

```python
import extension_module

ext(extension_module)
extension = ext("<extension uri>")

# access the extension module
module = extension.module
```

> An example to access and use extension module is at [here](https://github.com/StardustDL/coxbuild/blob/master/demo/ext.py).

## Extension URI

| Extension URI                                      | Description                                                  |
| -------------------------------------------------- | ------------------------------------------------------------ |
| `mod://{module name}`                              | Load from a Python module.                                   |
| `mod://{module name}@{module version}`             | Load from a Python module with specified version.            |
| `src@{hashcode}://{source code encoded in base64}` | Load from a Python source code (single file module).         |
| `file@{hashcode}://{file path}`                    | Load from a file (single file module).                       |
| `url@{hashcode}://{url}`                           | Load from a URL (single file module).                        |
| `ext@{hashcode}://{extension path}`                | Load from coxbuild extension gallery (CDN cached source).    |
| `ext@{hashcode}://{extension path}@{version}`      | Load from coxbuild extension gallery with specified version. |

> `@{hashcode}` is optional to check the checksum of the source code.

## Builtin Extensions

We provide a few extensions with coxbuild release package, in `coxbuild.extensions` module.

### Builtin

```python
from coxbuild.extensions import builtin
```

Builtin extension provides a few builtin tasks, event handlers, and hooks.

> This extension is automatically loaded when executing. No need to register it.

Builtin tasks:

| Name       | Description               |
| ---------- | ------------------------- |
| `:list`    | List all defined tasks    |
| `:serve`   | Start event-based service |
| `:ext`     | List all extensions       |
| `:project` | Print project settings    |
| `:default` | Builtin default task      |

### Python

```python
ext("mod://coxbuild.extensions.python.docs")
ext("mod://coxbuild.extensions.python.format")
ext("mod://coxbuild.extensions.python.package")
ext("mod://coxbuild.extensions.python.test")

from coxbuild.extensions.python import docs, format, package, test
```

### Shell

```python
ext("mod://coxbuild.extensions.shell")

from coxbuild.extensions import shell
```

### Node.js

```python
ext("mod://coxbuild.extensions.nodejs")

from coxbuild.extensions import nodejs
```

## .NET

```python
ext("mod://coxbuild.extensions.dotnet")

from coxbuild.extensions import dotnet
```

## Git

```python
ext("mod://coxbuild.extensions.git")

from coxbuild.extensions import git
```

## Gradle

```python
ext("mod://coxbuild.extensions.gradle")

from coxbuild.extensions import gradle
```

## Extension Gallery

We also provide a gallery of extensions in [exts](https://github.com/StardustDL/coxbuild-ext-gallery/).

A extension in the gallery is a single file `<name>.py`. The file is a valid Python module.

Access the extension file: `https://cdn.jsdelivr.net/gh/StardustDL/coxbuild-ext-gallery@<version>/exts/<name>.py`

You can use `ext://` URI to load the extension from the gallery.

For example, `ext://abc/module@0.0.1` will load the extension at `url://https://cdn.jsdelivr.net/gh/StardustDL/coxbuild-ext-gallery@0.0.1/exts/abc/module.py`

To configure the extension gallery, you can use the environment variable `COXBUILD_GALLERY=gal1;gal2`.

- GitHub: `github@reponame`
- Gitee: `gitee@reponame`
- Directory: `directory@/path/to/exts`
