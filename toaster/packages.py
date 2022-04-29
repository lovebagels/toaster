"""
Code for handling packages
"""
import os
import shutil
import json
import subprocess
import toml
from git import Repo
from bakery import get_all_packages
from utils import CloneProgress, dependingonsys, errecho, echo, secho
from exceptions import *


def remove_package(package):
    pkgs = get_all_packages()
    package_source = None
    package_dir = os.path.join('/opt/toaster/packages', package)

    if not os.path.exists(package_dir):
        raise NotFound

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound

    package_toml = toml.load(
        os.path.join('/opt/toaster/bakery', package_source, package, f'{package}.toml'))

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

    # Run "post_scripts"
    if dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
            subprocess.run(cmd)


def install_package(package):
    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound

    package_toml = toml.load(
        os.path.join('/opt/toaster/bakery', package_source, package, f'{package}.toml'))

    if 'build' in package_toml['types']:
        repo_dir = os.path.join('/opt/toaster/packages', package)

        if os.path.exists(repo_dir):
            raise AlreadyInstalled

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir,
                        progress=CloneProgress(package, git_url))

        wd = os.getcwd()

        os.chdir(repo_dir)

        # Run scripts
        if dependingonsys(package_toml['build'], 'scripts', append_mode=True):
            for cmd in dependingonsys(package_toml['build'], 'scripts', append_mode=True):
                subprocess.run(cmd)

        # Run make commands
        if dependingonsys(package_toml['build'], 'make_sudo'):
            secho(fg='bright_yellow')

        if dependingonsys(package_toml['build'], 'make', append_mode=True):
            for cmd in dependingonsys(package_toml['build'], 'make', append_mode=True):
                if dependingonsys(package_toml['build'], 'make_sudo'):
                    subprocess.run(['sudo', 'make'] + cmd)
                else:
                    subprocess.run(['make'] + cmd)

        # Run "post_scripts"
        if dependingonsys(package_toml['build'], 'post_scripts', append_mode=True):
            for cmd in dependingonsys(package_toml['build'], 'post_scripts', append_mode=True):
                subprocess.run(cmd)

        os.chdir(wd)
    else:
        raise NotImplementedError
