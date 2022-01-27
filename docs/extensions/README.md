# Extensions

A extension is just a Python module, which contains some tasks, event handlers, and hooks.

Use `loadext` function to load extension. The manager will traverse the extension module (no recursion) and register all the tasks, event handlers, and hooks.

> The member name with `_` prefix will be ignored.

```python
import extension_module

loadext(extension_module)
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