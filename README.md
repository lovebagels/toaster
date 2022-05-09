# Toaster - Simple macOS Package Manager

A simple package manager for macOS/Linux with support for binary packages and app bundles!

## Features and Goals

- Git-based package management
- Support binary packages and applications (.app packages)
- Support built-in Python 3
- Support x86_64 (x64) and ARM processors on both Linux and macOS
- Manages system updates on macOS

## Installation

### macOS

```bash
sh ./installer.sh
```

## Uninstall

***THIS WILL REMOVE ALL YOUR INSTALLED PACKAGES***

```bash
sh ./uninstaller.sh
```

## Installing Dependencies

`pip3 install atomicwrites click GitPython requests tqdm toml validators`
