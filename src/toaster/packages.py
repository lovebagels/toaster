"""
Code for handling packages
"""
import json
import os
import shutil
import subprocess
import tarfile
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


def get_package_loc(package):
    p = os.path.join(toaster_loc, 'packages')
    b = os.path.join(toaster_loc, 'binaries')
    a = os.path.join(toaster_loc, 'apps')

    if os.path.exists(p):
        return p

    if os.path.exists(b):
        return b

    if os.path.exists(a):
        return a

    raise NotFound


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

    try:
        package_toml = toml.load(os.path.join(
            toaster_loc, 'package_data', f'{package}.toml'))
    except FileNotFoundError:
        raise NotFound(package)

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

    # Delete broken symlinks
    clean_symlinks()


def build_package(repo_dir, package_dir, package_toml, link_warn=True, update=False):
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
                print(f'error running: {cmd}')

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


def install_package(package):
    """Install a package"""
    # try:
    #     shutil.rmtree(os.path.join(toaster_loc, '.cache'))
    # except:
    #     pass

    if not os.path.exists(os.path.join(toaster_loc, '.cache')):
        os.mkdir(os.path.join(toaster_loc, '.cache'))

    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound

    package_toml_loc = os.path.join(
        toaster_loc, 'bakery', package_source, package, f'{package}.toml')

    package_data_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    # Copy package TOML to package_data for uninstall and in case bakery is removed
    shutil.copyfile(package_toml_loc, package_data_loc)

    package_toml = toml.load(package_toml_loc)

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

        # Extract file
        if dependingonsys(package_toml['binary'], 'type') == 'gz':
            with tarfile.open(file_name) as f:
                f.extractall(package_dir)
        else:
            raise NotImplemented(
                f"Type {dependingonsys(package_toml['binary'], 'type')}")

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

    elif 'build' in package_toml['types']:
        repo_dir = os.path.join(toaster_loc, '.cache', package)
        package_dir = os.path.join(toaster_loc, 'packages', package)

        if os.path.exists(package_dir):
            raise AlreadyInstalled

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir,
                        progress=CloneProgress(package, git_url))

        build_package(repo_dir, package_dir, package_toml)
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
        raise NotFound

    package_toml_loc = os.path.join(
        toaster_loc, 'bakery', package_source, package, f'{package}.toml')

    package_data_loc = os.path.join(
        toaster_loc, 'package_data', f'{package}.toml')

    if not os.path.exists(package_data_loc):
        raise NotFound

    package_toml = toml.load(package_toml_loc)

    package_data_toml = toml.load(package_data_loc)

    if package_data_toml.get('version', None) == package_toml.get('version', None):
        raise AlreadyInstalled('Already up to date!')

    if 'build' in package_toml['types']:
        repo_dir = os.path.join(toaster_loc, '.cache', package)
        package_dir = os.path.join(toaster_loc, 'packages', package)

        if not os.path.exists(package_dir):
            raise NotFound

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir,
                        progress=CloneProgress(package, git_url))

        # Copy package TOML to package_data for uninstall and in case bakery is removed
        shutil.copyfile(package_toml_loc, package_data_loc)

        build_package(repo_dir, package_dir, package_toml,
                      link_warn=True, update=True)
    else:
        raise NotImplementedError
