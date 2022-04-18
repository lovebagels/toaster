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

## Reinstall

### macOS

```bash
sh ./uninstaller.sh && sh ./installer.sh
```

## Installing Dependencies

`pip3 install click atomicwrites requests tqdm GitPython toml`
