# Toaster - Simple macOS Package Manager

A simple package manager for macOS/Linux with support for binary packages and app bundles!

## Features and Goals

- Support binary packages and applications (.app packages)
- Support built-in Python 3 (in macOS Monterey, which is Python 3.8 right now) 
- Support x86_64 (x64) and ARM processors on both Linux and macOS
- Manages system updates on macOS
- Make it easy for users to add packages through the `toaster-users` source

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
