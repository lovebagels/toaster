# Toaster - Simple macOS/Linux Package Manager

***This is no where near ready yet and only currently supports building packages.***

A simple package manager for macOS/Linux with support for binary packages and app bundles!

## Features and Goals

- Installable on latest macOS without installing any additional things (besides pip packages)
- Support x86_64 (x64) and arm64 processors on both Linux and macOS
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
