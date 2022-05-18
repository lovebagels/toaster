# Making a Package

So, there's an application you want to add to toaster? or maybe you're just curious?

Well, either way, keep reading to know all you need to know about how toaster packages work.

## Package files

Every package has a TOML file named after the package, which describes how the package should be installed and uninstalled.

Here is an example of how a bakery (a git repo with packages in it) may be structured:

```tree
wxllow/toaster-core
├── _toaster.toml
├── coolexample
│   └── coolexample.toml
├── example
    └── example.toml
```

## Basic information

First in a package's TOML file is information like the name, version, license, dependencies, and which architectures/platforms it supports.

Here is an example of how this may look:

```toml
name = 'example'
desc = 'An example package.'
version = '1.0.0'
version_type = 'development'
license = "MIT"
archs = ['universal'] # Possible values: 'arm64', 'x86_64', 'universal'
linux_archs = ['any'] # Possible values: 'any', 'x86_64'
types = ['binary', 'build'] # Possible values: 'binary', 'build', 'app'
dependencies = ['python>3.8', 'go']
```

### Name and Description

The first 2 things here are the name (`name`) and description (`desc`), which are pretty self-explanatory.

### Version

Next is the version and the version type. These can be any string, but we recommend using a semantic version number and having version_type either be `stable`, `development`, `prototype`,`beta`, `alpha`, or something along those lines

## Homepage

A URL which has information about the package, can be anything.

### License

The license is pretty self-explanatory and can also be anything, but make sure that users are able to understand what the license means

### Archs (macOS)

Here you can specify which architectures you wish to target on macOS, either `universal`, `arm64`, or `x86_64`

### Archs (Linux)

Here, you can specify which architectures you wish to target on Linux... either `any` or `x86_64`

### Types

This is where you specify which type(s) your package supports. This can be `build`, `binary`, or `app`

`build` means an application that is built from source code

`binary` means a pre-built binary package

`app` means a GUI-only .app bundle ***(macOS only)***

### Dependencies

Here is where you can place all the other packages you require to be installed to install your package. You can specify just a package's name, like `go`, or a minimum version to be required for the package, like `python>=3.7`.

### Use

Here is where you can put a list of commands not installable from toaster that are required to install your program.

## Binary

Here is an example of a simple binary program's TOML file

The package in question is Go.

```toml
[binary]
type = 'gz'
link_dirs = ['go/bin']

    [[binary.arm64]]
    url = 'https://storage.googleapis.com/golang/go1.16.darwin-arm64.tar.gz'

    [[binary.x86_64]]
    url = 'https://storage.googleapis.com/golang/go1.16.darwin-amd64.tar.gz'

```

### URL

First and most importantly is the URL. This is a file archive (`.zip`, `tar.gz`, etc.)

This file is downloaded and then extracted to the package's directory

### Type

This is the type of archive you specified in the URL. (`zip`, `gz`, `xz`, etc.)

### Link Dirs

List of directorys that you wish to be linked to PATH after installation. Paths are relative to the package directory ({prefix}). Defaults to `['bin']`

## Build

Here is an example

```toml
[build]
repo = 'https://github.com/foo/bar'
branch = 'master'
format_scripts = true
scripts = [['./configure', '--prefix {prefix}'], [['make'], ['install']]]
link_dirs = ['bin']

# Indentation is optional btw :)
    [[build.universal]]
    scripts = [['echo', 'hello, apple!']]
    post_scripts = [['echo', 'hello again, apple!']]

    [[build.uninstall]]
        [[build.uninstall.universal]]
        scripts = [['echo', 'bye bye, apple!']]
```

### Repository

The first two items here tell toaster which Git repo to download the source code from and which branch of that repo to use.

### Format Scripts?

This is a boolean which tells toaster whether it should format scripts with things like {prefix} which contain data, such as where the package should be installed, in the case of {prefix}.

### Link dirs

List of directorys that you wish to be linked to PATH after installation. Paths are relative to the package directory ({prefix}). Defaults to `['bin']`

### Scripts

These are scripts to run during installation **in the temp directory with the package's source code**.

This could be things like `./configure --prefix {prefix}`

This should be a list containing commands to run. Commands should also be a list, seperated by their arguments. For example, `[['./configure', '--prefix {prefix}'], ['make', 'install']]`. This is for security reasons. If you have experience with for example the subprocess library on Python, you are likely already be familiar with this.

### Post-scripts

These are scripts that are run right before installation is finished and are ran in the project directory. These work the same as regular scripts, just ran at a different time and in a different directory.

## Platform-Specific Instructions

Platform/architecture specific instructions can be used. These will either overwrite their general values or append them (if the item is a list)

For example:

```toml
    [[build.universal]]
    scripts = [['echo', 'hello, apple!']]
    post_scripts = [['echo', 'hello again, apple!']]

    [[build.linux_any]]
    scripts = [['echo', 'hello, tux!']]
    post_scripts = [['echo', 'hello again, tux!']
```
