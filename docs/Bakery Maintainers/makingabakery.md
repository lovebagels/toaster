# Making a Bakery

Bakeries are git repositories which serve as "sources" which contain instructions for downloading/installing packages. Users can make their own bakeries whether it be for their own packages, other people's packages, or both.

## Package files

Here is an example of how a bakery may be structured:

```tree
wxllow/toaster-core
├── _toaster.toml
├── go
│   └── go.toml
├── python
│   └── python.toml
├── python@2.7
    └── python@2.7.toml
```

## _toaster.toml

Bakeries should have a file in the root directory named `_toaster.toml`. This is a TOMl file which defines basic information about a bakery.

Here is an example `_toaster.toml` file:

```toml
name = 'core'
maintainer = 'wxllow'
description = 'Core toaster packages!'
```

## Packages

Package instructions (package TOMLs) should be in a directory in the root directory, named whatever the package's name shall be. In this directory should be a TOML file with the same name as the directory (which shall be the package's name).
