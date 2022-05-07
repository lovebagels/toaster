"""
Code for handling packages
"""
from exceptions import *
from utils import CloneProgress, dependingonsys, where_is_toaster, errecho, echo, secho
from bakery import get_all_packages
from git import Repo
import os
import shutil
import json
import subprocess
import toml
from pathlib import Path


toaster_loc = where_is_toaster()


def clean_symlinks():
    """Cleans left over symbolic links from uninstalled/updated packages"""
    bin_dir = os.path.join(toaster_loc, 'bin')

    for filename in os.listdir(bin_dir):
        file = os.path.join(bin_dir, filename)

        if not os.path.exists(os.readlink(file)):
            os.remove(file)


def remove_package(package):
    """Remove/uninstall a package"""
    pkgs = get_all_packages()
    package_source = None
    package_dir = os.path.join(toaster_loc, 'packages', package)

    if not os.path.exists(package_dir):
        raise NotFound

    package_toml = toml.load(os.path.join(
        toaster_loc, 'package_data', f'{package}.toml'))

    if 'uninstall' in package_toml['build']:
        # Run scripts
        if dependingonsys(package_toml['build']['uninstall'], 'scripts', append_mode=True):
            for cmd in dependingonsys(package_toml['build']['uninstall'], 'scripts', append_mode=True):
                subprocess.run(cmd)

        # Run make commands
        if dependingonsys(package_toml['build']['uninstall'], 'make', append_mode=True):
            for cmd in dependingonsys(package_toml['build']['uninstall'], 'make', append_mode=True):
                if dependingonsys(package_toml['build']['uninstall'], 'make_sudo'):
                    subprocess.run(['sudo', 'make'] + cmd)
                else:
                    subprocess.run(['make'] + cmd)

    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    if 'uninstall' in package_toml['build']:
        # Run "post_scripts"
        if dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
            for cmd in dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
                subprocess.run(cmd)

    # Delete broken symlinks
    clean_symlinks()


def install_package(package):
    """Install a package"""
    try:
        shutil.rmtree(os.path.join(toaster_loc, '.cache'))
    except:
        pass

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

    package_toml = toml.load(os.path.join(
        toaster_loc, 'bakery', package_source, package, f'{package}.toml'))

    if 'build' in package_toml['types']:
        repo_dir = os.path.join(toaster_loc, '.cache', package)
        package_dir = os.path.join(toaster_loc, 'packages', package)

        if os.path.exists(package_dir):
            raise AlreadyInstalled

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir,
                        progress=CloneProgress(package, git_url))

        wd = os.getcwd()

        os.chdir(repo_dir)

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
            package_toml['build'], '', append_mode=True) or ['bin']

        try:
            for ld in link_dirs:
                ld = os.path.join(package_dir, ld)

                if os.path.isdir(ld):
                    for filename in os.listdir(ld):
                        os.symlink(os.path.join(ld, filename),
                                   os.path.join(toaster_loc, 'bin', filename))
        except FileExistsError:
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
    else:
        raise NotImplementedError
