"""
Code for handling packages
"""
import os
from asyncio import subprocess
from repos import get_all_packages
import toml
import subprocess
from git import Repo
from exceptions import *
from utils import CloneProgress, dependingonsys
from pathlib import Path
import shutil


def remove_package(package):
    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound

    package_toml = toml.load(
        f'/opt/toaster/sources/{package_source}/{package}/{package}.toml')

    # Run "pre_scripts"
    if dependingonsys(package_toml['build']['uninstall'], 'pre_scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['build']['uninstall'], 'pre_scripts', append_mode=True):
            subprocess.run(cmd)

    # Run make commands
    if dependingonsys(package_toml['build']['uninstall'], 'make', append_mode=True):
        for cmd in dependingonsys(package_toml['build']['uninstall'], 'make', append_mode=True):
            if dependingonsys(package_toml['build']['uninstall'], 'make_sudo'):
                subprocess.run(['sudo', 'make'] + cmd)
            else:
                subprocess.run(['make'] + cmd)

    # Run "post_scripts"
    if dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['build']['uninstall'], 'post_scripts', append_mode=True):
            subprocess.run(cmd)

    if os.path.exists(f'/opt/toaster/packages/{package}'):
        shutil.rmtree(f'/opt/toaster/packages/{package}')
    else:
        raise NotFound


def install_package(package):
    pkgs = get_all_packages()
    package_source = None

    for key in pkgs:
        if package in pkgs[key]:
            package_source = key

    if not package_source:
        raise NotFound

    package_toml = toml.load(
        f'/opt/toaster/sources/{package_source}/{package}/{package}.toml')

    if 'build' in package_toml['info']['types']:
        repo_dir = f'/opt/toaster/packages/{package}'

        if os.path.exists(repo_dir):
            raise AlreadyInstalled

        git_url = dependingonsys(package_toml['build'], 'repo')

        if not git_url:
            raise Exception('No repo in TOML')

        Repo.clone_from(git_url, repo_dir,
                        progress=CloneProgress(package, git_url))

        wd = os.getcwd()

        os.chdir(repo_dir)

        # Run "pre_scripts"
        if dependingonsys(package_toml['build'], 'pre_scripts', append_mode=True):
            for cmd in dependingonsys(package_toml['build'], 'pre_scripts', append_mode=True):
                subprocess.run(cmd)

        # Run make commands
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
