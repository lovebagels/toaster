"""
Code for handling packages
"""
import json
import os
import shutil
import subprocess
import tarfile
import zipfile
from ast import If
from functools import cache
from pathlib import Path

import toml
from bakery import get_all_packages
from exceptions import *
from git import Repo
from utils import CloneProgress
from utils import dependingonsys
from utils import download_file
from utils import echo
from utils import errecho
from utils import secho
from utils import where_is_toaster


toaster_loc = where_is_toaster()


# Package Info
def get_info(package):
    toml_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    if not os.path.exists(toml_loc):
        pkgs = get_all_packages()
        package_source = None

        for key in pkgs:
            if package in pkgs[key]:
                package_source = key

        if not package_source:
            raise NotFound(package)

        toml_loc = os.path.join(toaster_loc, 'bakery',
                                package_source, package, f'{package}.toml')

    return toml.load(toml_loc)


def get_dependants(package):
    """Get list of installed packages that depend on a package"""
    l = []

    package_data_loc = os.path.join(
        toaster_loc, 'package_data')

    for filename in os.listdir(package_data_loc):
        package_toml = toml.load(os.path.join(
            package_data_loc, filename))

        # print(package_toml)

        if package in package_toml.get('dependencies', []):
            l.append(filename.split('.')[0])

    return l


def install_dependencies(dependencies, out=True):
    """Install dependencies for a package"""
    for dependency in dependencies:
        dependency = dependency.split('>=')[0]

        try:
            install_package(dependency, ignore_dependencies=True)
        except AlreadyInstalled as e:
            if out:
                secho(
                    f'Dependency {dependency} is already installed, ignoring!', fg='bright_black')
                return

            raise e


def get_package_loc(package):
    """Get the location of a package"""
    p = os.path.join(toaster_loc, 'packages', package)
    b = os.path.join(toaster_loc, 'binaries', package)
    a = os.path.join(toaster_loc, 'apps', package)

    if os.path.exists(p):
        return p

    if os.path.exists(b):
        return b

    if os.path.exists(a):
        return a

    raise NotFound(package)


def clean_symlinks():
    """Cleans left over symbolic links from uninstalled/updated packages"""
    bin_dir = os.path.join(toaster_loc, 'bin')

    for filename in os.listdir(bin_dir):
        file = os.path.join(bin_dir, filename)

        if not os.path.exists(os.readlink(file)):
            os.remove(file)


def remove_package(package):
    """Remove/uninstall a package"""
    package_dir = get_package_loc(package)
    package_toml_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    try:

        package_toml = toml.load(package_toml_loc)
    except FileNotFoundError:
        raise NotFound(package)

    dependants = get_dependants(package)

    if dependants:
        raise Exception(f'This package is depended on by {len(dependants)}!')

    if 'build' in package_toml['types']:
        if 'uninstall' in package_toml['build']:
            # Run scripts
            if dependingonsys(package_toml['build']['uninstall'], 'scripts', append_mode=True):
                for cmd in dependingonsys(package_toml['build']['uninstall'], 'scripts', append_mode=True):
                    subprocess.run(cmd)

            # Run "post_scripts"
            if dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
                for cmd in dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
                    subprocess.run(cmd)

    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    if os.path.exists(package_toml_loc):
        os.remove(package_toml_loc)

    # Delete broken symlinks
    clean_symlinks()


def _build_package(repo_dir, package_dir, package_toml, link_warn=True, update=False):
    """Build/install a package"""
    wd = os.getcwd()

    os.chdir(repo_dir)

    if update:
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)

    # Make package dir and package/bin dir
    os.mkdir(package_dir)
    os.mkdir(os.path.join(package_dir, 'bin'))

    # Run scripts
    if dependingonsys(package_toml['build'], 'scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['build'], 'scripts', append_mode=True):
            # Format scripts
            if dependingonsys(package_toml['build'], 'format_scripts'):
                cmdnew = []

                for i in cmd:
                    cmdnew.append(
                        i.format(prefix=package_dir))

                cmd = cmdnew

            try:
                subprocess.run(cmd)
            except:
                errecho(f'error running: {cmd}')

    # Delete temp cache dir
    shutil.rmtree(repo_dir)

    # Link package binaries to toaster/bin
    link_dirs = dependingonsys(
        package_toml['build'], 'link_dirs', append_mode=True) or ['bin']

    try:
        for ld in link_dirs:
            ld = os.path.join(package_dir, ld)

            if os.path.isdir(ld):
                for filename in os.listdir(ld):
                    os.symlink(os.path.join(ld, filename),
                               os.path.join(toaster_loc, 'bin', filename))
    except FileExistsError:
        if link_warn:
            secho("1 or more links already exist and were not linked.",
                  fg='bright_black')

    os.chdir(package_dir)

    # Run "post_scripts"
    if dependingonsys(package_toml['build'], 'post_scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['build'], 'post_scripts', append_mode=True):
            # Format scripts
            if dependingonsys(package_toml['build'], 'format_scripts'):
                cmdnew = []

                for i in cmd:
                    cmdnew.append(i.format(prefix=package_dir))

                cmd = cmdnew

            subprocess.run(cmd)

    os.chdir(wd)


def _install_binary(package, package_dir, file_name, package_toml):
    """Installs a binary package"""
    # Extract file
    type = dependingonsys(package_toml['binary'], 'type').strip().lower()

    if type in ['tar', 'gz', 'xz']:
        with tarfile.open(file_name) as f:
            f.extractall(package_dir)
    elif type == 'zip':
        with zipfile.ZipFile(file_name, 'r') as f:
            f.extractall(package_dir)
    else:
        msg = f"Unknown archive type: {dependingonsys(package_toml['binary'], 'type')}"
        raise NotImplemented(msg)

    link_warn = True

    # Link package binaries to toaster/bin
    link_dirs = dependingonsys(
        package_toml['binary'], 'link_dirs', append_mode=True) or ['bin']

    try:
        for ld in link_dirs:
            ld = os.path.join(package_dir, ld)

            if os.path.isdir(ld):
                for filename in os.listdir(ld):
                    os.symlink(os.path.join(ld, filename),
                               os.path.join(toaster_loc, 'bin', filename))
    except FileExistsError:
        if link_warn:
            secho("1 or more links already exist and were not linked.",
                  fg='bright_black')


def install_package(package, ignore_dependencies=False):
    """Install a package"""
    if not os.path.exists(os.path.join(toaster_loc, '.cache')):
        os.mkdir(os.path.join(toaster_loc, '.cache'))

    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound(package)

    package_toml_loc = os.path.join(
        toaster_loc, 'bakery', package_source, package, f'{package}.toml')

    package_data_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    # Copy package TOML to package_data for uninstall and in case bakery is removed
    shutil.copyfile(package_toml_loc, package_data_loc)

    package_toml = toml.load(package_toml_loc)

    if not ignore_dependencies:
        install_dependencies(dependingonsys(
            package_toml, 'dependencies', append_mode=True)
        )

    if 'binary' in package_toml['types']:
        download_url = dependingonsys(package_toml['binary'], 'url')
        package_dir = os.path.join(toaster_loc, 'binaries', package)
        cache_dir = os.path.join(toaster_loc, '.cache', package)

        if os.path.exists(package_dir):
            raise AlreadyInstalled

        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir, 0o777)

        file_name = os.path.join(cache_dir, download_url.split("/")[-1])

        if not os.path.exists(file_name):
            download_file(
                download_url, file_name
            )

        _install_binary(package, package_dir, file_name, package_toml)

    elif 'build' in package_toml['types']:
        repo_dir = os.path.join(toaster_loc, '.cache', package)
        package_dir = os.path.join(toaster_loc, 'packages', package)

        if os.path.exists(package_dir):
            raise AlreadyInstalled

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir, branch=(dependingonsys(
            package_toml['builf'], 'branch') or 'master'), progress=CloneProgress(package, git_url))

        _build_package(repo_dir, package_dir, package_toml)
    else:
        raise NotImplementedError


def update_package(package):
    """Update a package"""
    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound(package)

    package_toml_loc = os.path.join(
        toaster_loc, 'bakery', package_source, package, f'{package}.toml')

    package_data_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    if not os.path.exists(package_data_loc):
        raise NotFound(package)

    package_toml = toml.load(package_toml_loc)

    package_data_toml = toml.load(package_data_loc)

    if package_data_toml.get('version', None) == package_toml.get('version', None):
        raise AlreadyInstalled('Already up to date!')

    if 'build' in package_toml['types']:
        repo_dir = os.path.join(toaster_loc, '.cache', package)
        package_dir = os.path.join(toaster_loc, 'packages', package)

        if not os.path.exists(package_dir):
            raise NotFound(package)

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir, branch=(dependingonsys(
            package_toml['builf'], 'branch') or 'master'), progress=CloneProgress(package, git_url))

        # Copy package TOML to package_data for uninstall and in case bakery is removed
        shutil.copyfile(package_toml_loc, package_data_loc)

        _build_package(repo_dir, package_dir, package_toml,
                       link_warn=True, update=True)
    else:
        raise NotImplementedError
