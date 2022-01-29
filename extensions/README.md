# Extensions

An extension is a wrapped Python module, which contains some tasks, event handlers, and hooks.

Use `ext` function to register extension by a loaded module or an extension URI. It will load and register the extension and then return it.

| Extension URI                                      | Description                                          |
| -------------------------------------------------- | ---------------------------------------------------- |
| `module://{module name}@{module version}`          | Load from a Python module with specified version.    |
| `module://{module name}`                           | Load from a Python module with unspecified version.  |
| `src@{hashcode}://{source code encoded in base64}` | Load from a Python source code (single file module). |
| `file@{hashcode}://{file path}`                    | Load from a file (single file module).               |
| `url@{hashcode}://{url}`                           | Load from a URL (single file module).                |

> `@{hashcode}` is optional to check the checksum of the source code.

```python
import extension_module

ext(extension_module)
extension = ext("<extension uri>")

# access the extension module
module = extension.module
```

> An example to access and use extension module is at [here](https://github.com/StardustDL/coxbuild/blob/master/demo/ext.py).

When executing, the manager will traverse the extension module (no recursion) and register all the tasks, event handlers, and hooks.

> The member name with `_` prefix will be ignored.


## Python

```python
import coxbuild.extensions.python.docs
import coxbuild.extensions.python.format
import coxbuild.extensions.python.package
import coxbuild.extensions.python.test
```

## Shell

```python
import coxbuild.extensions.shell
```

## Node.js

```python
import coxbuild.extensions.nodejs
```

## .NET

```python
import coxbuild.extensions.dotnet
```

## Git

```python
import coxbuild.extensions.git
```

## Gradle

```python
import coxbuild.extensions.gradle
```