# Extensions

A extension is a wrapped Python module, which contains some tasks, event handlers, and hooks.

Use `ext` function to register extension by a loaded module or an extension URI. The manager will traverse the extension module (no recursion) and register all the tasks, event handlers, and hooks.

> The member name with `_` prefix will be ignored.

| Extension URI                           | Description                                         |
| --------------------------------------- | --------------------------------------------------- |
| `module://[moduleName]@[moduleVersion]` | Load from a Python module with specified version.   |
| `module://[moduleName]`                 | Load from a Python module with unspecified version. |
| `file://[filePath]`                     | Load from a file.                                   |
| `url://[url]`                           | Load from a URL.                                    |

```python
import extension_module

ext(extension_module)
ext("<extension uri>")
```


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