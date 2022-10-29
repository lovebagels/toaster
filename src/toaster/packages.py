"""
Code for handling packages
"""
import json
import os
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

import toml
from bakery import get_all_packages
from exceptions import *
from git import Repo
from packaging import version
from utils import CloneProgress
from utils import dependingonsys
from utils import download_file
from utils import echo
from utils import errecho
from utils import secho
from utils import where_is_toaster


toaster_loc = where_is_toaster()


# Package Info
def get_info(package, from_installed=True, from_bakery=True):
    """Returns a packages TOML file either installed or from a bakery."""
    toml_loc = None

    if from_installed:
        l = os.path.join(
            toaster_loc, 'package_data', f'{package}.toml')

        if os.path.exists(l):
            toml_loc = l
            from_bakery = False

    if from_bakery:
        pkgs = get_all_packages()
        package_source = None

        for key in pkgs:
            if package in pkgs[key]:
                package_source = key

        if not package_source:
            raise NotFound(package)

        l = os.path.join(toaster_loc, 'bakery',
                         package_source, package, f'{package}.toml')

        if os.path.exists(l):
            toml_loc = l

    if not toml_loc:
        raise NotFound(package)

    return toml.load(toml_loc)


def get_dependants(package):
    """Get list of installed packages that depend on a package"""
    l = []

    package_data_loc = os.path.join(
        toaster_loc, 'package_data')

    for filename in os.listdir(package_data_loc):
        package_toml = toml.load(os.path.join(
            package_data_loc, filename))

        if package in dependingonsys(package_toml, 'dependencies', append_mode=True):
            l.append(filename.split('.')[0])

    return l


def install_dependencies(dependencies, out=True):
    """Install dependencies for a package"""
    for dependency in dependencies:
        try:
            secho(f"Installing dependency: {dependency}", fg="bright_magenta")
            install_package(dependency)

        except AlreadyInstalled as e:
            if out:
                secho(
                    f'Dependency {dependency} is already installed, ignoring!', fg='bright_black')

            return

        secho(f'Installed dependency: {dependency}', fg="bright_magenta")


def get_package_loc(package):
    """Get the location of an installed package"""
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


def make_symlinks(package_toml, package_dir, link_warn=True, force=False):
    """Makes symlinks"""
    # Link package binaries to toaster/bin
    link_dirs = dependingonsys(
        package_toml, 'link_dirs', append_mode=True) or ['bin']

    try:
        for ld in link_dirs:
            ld = os.path.join(package_dir, ld)

            if os.path.isdir(ld):
                for filename in os.listdir(ld):
                    if not force:
                        if shutil.which(os.path.split(filename)[-1]):
                            raise FileExistsError

                    link_loc = os.path.join(toaster_loc, 'bin', filename)

                    if force:
                        if os.path.exists(link_loc):
                            os.remove(link_loc)

                    os.symlink(os.path.join(ld, filename), link_loc)
    except FileExistsError:
        if link_warn:
            secho("1 or more links already exist and were not linked. You can force links using `toaster link --force package`",
                  fg='bright_black')


def remove_symlinks(package_toml, package_dir):
    """Deletes symlinks"""
    # Unlink package binaries to toaster/bin
    link_dirs = dependingonsys(
        package_toml, 'link_dirs', append_mode=True) or ['bin']

    for ld in link_dirs:
        ld = os.path.join(package_dir, ld)

        if os.path.isdir(ld):
            for filename in os.listdir(ld):
                loc = os.path.join(toaster_loc, 'bin', filename)

                if os.path.exists(loc):
                    os.remove(loc)


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
        raise DependedOnError(package, dependants)

    if 'binary' in package_toml['types']:
        if 'uninstall' in package_toml['binary']:
            # Run scripts
            if dependingonsys(package_toml['binary']['uninstall'], 'scripts', append_mode=True):
                for cmd in dependingonsys(package_toml['binary']['uninstall'], 'scripts', append_mode=True):
                    subprocess.run(cmd)

            # Run "post_scripts"
            if dependingonsys(package_toml['binary']['uninstall'], 'post_scripts', append_mode=True):
                for cmd in dependingonsys(package_toml['binary']['uninstall'], 'post_scripts', append_mode=True):
                    subprocess.run(cmd)
    elif 'build' in package_toml['types']:
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


def _tar_members(base, tar, strip=1):
    members = []

    for member in tar.getmembers():
        p = Path(member.path)
        member.path = os.path.join(
            base, p.relative_to(*p.parts[:strip]))
        members.append(member)

    return members


def _extract_tar(path, file_name):
    with tarfile.open(file_name) as f:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(f, members=_tar_members(path,f))


def _build_package(repo_dir, package_dir, package_toml, file_name=None, is_git=True, link_warn=True, update=False):
    """Build/install a package"""
    wd = os.getcwd()

    if update:
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)

    # Make package dir and package/bin dir
    os.mkdir(package_dir)
    os.mkdir(os.path.join(package_dir, 'bin'))

    if not is_git:
        repo_dir = os.path.join(
            toaster_loc, '.cache', f'extracted{os.path.split(file_name)[-1]}')

        # Extract file
        archive_type = dependingonsys(
            package_toml['build'], 'type').strip().lower()

        if archive_type in ['tar', 'gz', 'xz']:
            _extract_tar(repo_dir, file_name)
        elif archive_type == 'zip':
            with zipfile.ZipFile(file_name, 'r') as f:
                f.extractall(repo_dir)
        else:
            msg = f"Unknown archive type: {dependingonsys(package_toml['build'], 'type')}"
            raise NotImplemented(msg)

        link_warn = True

    os.chdir(repo_dir)

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

    link_warn = True

    make_symlinks(package_toml['build'], package_dir, link_warn)

    os.chdir(wd)


def _install_binary(package, package_dir, file_name, package_toml, link_warn=True):
    """Installs a binary package"""
    # Extract file
    archive_type = dependingonsys(
        package_toml['binary'], 'type').strip().lower()

    if archive_type in ['tar', 'gz', 'xz']:
        _extract_tar(package_dir, file_name)
    elif archive_type == 'zip':
        with zipfile.ZipFile(file_name, 'r') as f:
            f.extractall(package_dir)
    else:
        msg = f"Unknown archive type: {dependingonsys(package_toml['binary'], 'type')}"
        raise NotImplemented(msg)

    os.chdir(package_dir)

    # Run scripts
    if dependingonsys(package_toml['binary'], 'scripts', append_mode=True):
        for cmd in dependingonsys(package_toml['binary'], 'scripts', append_mode=True):
            # Format scripts
            if dependingonsys(package_toml['binary'], 'format_scripts'):
                cmdnew = []

                for i in cmd:
                    cmdnew.append(
                        i.format(prefix=package_dir))

                cmd = cmdnew

            try:
                subprocess.run(cmd)
            except:
                errecho(f'error running: {cmd}')

    make_symlinks(package_toml['binary'], package_dir, link_warn)


def install_package(package_name, ignore_dependencies=False):
    """Install a package"""
    package = package_name.split('>=')[0]

    package_minver = None

    if len(package_name.split('>=')) > 1:
        package_minver = package_name.split('>=')[1]

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

    if package_minver:
        if version.parse(package_minver) > version.parse(package_toml.get('version', 0)):
            raise NotFound(
                f'Could not meet minimum version requirement {package_minver} for {package}')

    if not ignore_dependencies:
        install_dependencies(dependingonsys(
            package_toml, 'dependencies', append_mode=True)
        )

    for use in dependingonsys(package_toml, 'use', append_mode=True):
        if not shutil.which(use):
            raise UseNotFound(use)

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
        url = dependingonsys(package_toml['build'], 'url')

        file_name = None

        is_git = bool(git_url)

        if git_url:
            Repo.clone_from(git_url, repo_dir, branch=(dependingonsys(
                package_toml['build'], 'branch') or 'master'), progress=CloneProgress(package, git_url))
        elif url:
            cache_dir = os.path.join(toaster_loc, '.cache')

            file_name = os.path.join(cache_dir, url.split("/")[-1])

            if not os.path.exists(file_name):
                download_file(url, file_name)
        else:
            raise Exception('No where to download package from')

        _build_package(repo_dir, package_dir, package_toml, file_name, is_git)
    else:
        raise NotImplementedError


def update_all_packages():
    """Update all packages"""
    for t in ['packages', 'binaries', 'apps']:
        for package in os.listdir(os.path.join(toaster_loc, t)):
            try:
                update_package(package)
            except:
                continue


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
            package_toml['build'], 'branch') or 'master'), progress=CloneProgress(package, git_url))

        # Copy package TOML to package_data for uninstall and in case bakery is removed
        shutil.copyfile(package_toml_loc, package_data_loc)

        _build_package(repo_dir, package_dir, package_toml,
                       link_warn=True, update=True)
    else:
        raise NotImplementedError
