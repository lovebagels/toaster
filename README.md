# Toaster - Simple macOS/Linux Package Manager

***This is no where near ready yet and only currently supports building packages.***

A simple package manager for macOS/Linux with support for binary packages and app bundles! (in addition to built packages)

Toaster also runs on other UNIX-like systems (though unofficially)

## Features and Goals

- Installable on latest macOS without installing any additional things (besides PIP packages)
- Support x86_64 (x64) and arm64 processors on both Linux and macOS
- Store everything in a user directory (so no need to use root)
- Don't store extra cache that isn't needed (unless the user specifies that)
- Manages system updates on macOS
- Don't bloat users storage with unnecessary caching, only cache what's needed.

## Install

```bash
sh <(curl -L https://bagels.sh)
```

## Uninstall

```bash
sh <(curl -L https://uninstall.bagels.sh)
```

## Docs

View the docs at <https://docs.bagels.sh>
