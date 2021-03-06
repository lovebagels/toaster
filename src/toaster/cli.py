#!/usr/bin/env python3
import platform
import sys
from urllib.parse import urlparse

import click
import sysupdates
import validators
from bakery import add_bakery
from bakery import refresh_bakeries
from bakery import rm_bakery
from click_aliases import ClickAliasedGroup
from exceptions import *
from packages import get_all_packages
from packages import get_info as get_package_info
from packages import get_package_loc
from packages import install_package
from packages import make_symlinks
from packages import remove_package
from packages import remove_symlinks
from packages import update_all_packages
from packages import update_package
from utils import echo
from utils import errecho
from utils import secho
from utils import update_toaster


# https://stackoverflow.com/a/58770064
class GroupedGroup(ClickAliasedGroup):
    def command(self, *args, **kwargs):
        """Gather the command help groups"""
        help_group = kwargs.pop('group', None)
        decorator = super().command(*args, **kwargs)

        def wrapper(f):
            cmd = decorator(f)
            cmd.help_group = help_group
            return cmd

        return wrapper

    def format_commands(self, ctx, formatter):
        # Modified fom the base class method

        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if not (cmd is None or cmd.hidden):
                commands.append((subcommand, cmd))

        if commands:
            longest = max(len(cmd[0]) for cmd in commands)
            # allow for 3 times the default spacing
            limit = formatter.width - 6 - longest

            groups = {}
            for subcommand, cmd in commands:
                help_str = cmd.get_short_help_str(limit)
                subcommand += ' ' * (longest - len(subcommand))
                groups.setdefault(
                    cmd.help_group, []).append((subcommand, help_str))

            with formatter.section('Commands'):
                for group_name, rows in groups.items():
                    with formatter.section(group_name or 'Other'):
                        formatter.write_dl(rows)


@click.group(cls=GroupedGroup)
def cli():
    pass


def refresh_db(auto=False):
    """Refresh bakeries (this is for commands to use)"""
    msg = 'Refreshing bakeries...'

    if auto:
        msg = 'Automatically refreshing bakeries...'

    secho(
        f':: {msg}', fg='bright_magenta')
    refresh_bakeries()
    secho(
        'Bakeries updated :)', fg='bright_green')


@cli.command(help='Refresh bakeries', group='Bakeries')
def refresh():
    """Refresh bakeries"""
    refresh_db()


@cli.command(help='Add bakeries', group='Bakeries')
@click.argument('bakeries', nargs=-1, required=True, type=str)
def bakery(bakeries):
    """Add a bakery"""
    for bakery in bakeries:
        if validators.url(bakery):
            # Git url
            name = '/'.join(urlparse(bakery).path.split(
                '/')[-2:])
            loc = bakery
        elif len(bakery.split('/')) == 2:
            # Github URL possibly
            name = bakery
            loc = f'https://github.com/{bakery}'
        elif len(bakery.split(':')) > 1:
            # Local file
            name = bakery.split(':', maxsplit=2)[0]
            loc = bakery.split(':', maxsplit=2)[1]
        else:
            return errecho(f"I don't know how to add {bakery} :(!")

        name = name.replace('toaster-', '')

        secho(
            f':: Adding {name}...', fg='bright_magenta')
        add_bakery(name, loc)
        secho(f'Bakery {name} added!', fg='bright_green')


@cli.command(help='Remove bakeries', group='Bakeries')
@click.argument('bakeries', nargs=-1, required=True, type=str)
def unbake(bakeries):
    """Remove a bakery"""
    for bakery in bakeries:
        if validators.url(bakery):
            # Git url
            name = '/'.join(urlparse(bakery).path.split(
                '/')[-2:])
            loc = bakery
        elif len(bakery.split('/')) == 2:
            # Github URL possibly
            name = bakery
            loc = f'https://github.com/{bakery}'
        elif len(bakery.split(':')) > 1:
            # Local file
            name = bakery.split(':', maxsplit=2)[0]
            loc = bakery.split(':', maxsplit=2)[1]
        else:
            return errecho(f"I don't know how to add {bakery} :(!")

        name = name.replace('toaster-', '')

        secho(
            f':: Removing {name}...', fg='bright_magenta')

        try:
            rm_bakery(name, loc)
        except KeyError:
            return errecho(f"{name} doesn't exist.")

        secho(f'Bakery {name} removed!', fg='bright_green')


@cli.command(help='Get info about packages', group='Packages')
@click.argument('packages', nargs=-1, required=True, type=str)
def info(packages):
    """Get info about a package"""
    for package in packages:
        try:
            package_toml = get_package_info(package)
        except NotFound:
            errecho(f'{package} could not be found.')
        else:
            secho(
                f"::: {package_toml.get('name', package)} {package_toml.get('version', '')} :::", fg='bright_magenta')

            secho(f"{package_toml.get('desc', 'No description.')}",
                  fg='bright_black')

            if package_toml.get('homepage'):
                secho(f"Homepage: {package_toml.get('homepage', 'None')}\n",
                      fg='bright_blue')

            # Version info
            secho(
                f"Version: {package_toml.get('version', 'Unknown')}", fg='bright_yellow')
            secho(
                f"Version type: {package_toml.get('version_type', 'Unknown').title()}\n", fg='bright_yellow')

            # License
            secho(
                f"License: {package_toml.get('license', 'Unknown')}\n", fg='bright_yellow')

            # Architectures
            if platform.system() != 'Darwin':
                archs = package_toml.get("linux_archs", [])
            else:
                archs = package_toml.get("archs", [])

            secho(
                f"Architectures: {', '.join(archs) or 'None'}", fg='green')


@cli.command(help='Install packages', group='Packages')
@click.argument('packages', nargs=-1, required=True, type=str)
@click.option('--refresh', help='Refresh Packages', default=True)
def install(packages, refresh):
    """Install a package"""
    if refresh:
        refresh_db(auto=True)

    for package in packages:
        secho(
            f':: Installing {package}...', fg='bright_magenta')

        try:
            install_package(package)
        except NotFound:
            errecho(f'{package} could not be found.')
        except AlreadyInstalled:
            errecho(
                f'{package} is already installed. Do `toaster reinstall {package}` to reinstall.')
        except NotImplementedError:
            errecho(
                f'{package} was found but is not available because it is a binary or app which is not supported yet.')
        except UseNotFound as e:
            errecho(
                f'{package} requires the external dependency `{e}`, which could not be found!')
        else:
            secho(
                f'{package} installed!', fg='bright_green')


@cli.command(help='Remove packages', aliases=['uninstall'], group='Packages')
@click.argument('packages', nargs=-1, required=True, type=str)
def remove(packages):
    """Remove a package"""
    for package in packages:
        secho(
            f':: Remoivng {package}...', fg='bright_magenta')
        try:
            remove_package(package)
        except NotFound:
            errecho(f'{package} is not installed.')
            return
        except DependedOnError as e:
            errecho(
                f'{package} is depended on by {len(e.args[1])} packages!')
            return
        secho(
            f'Removed {package}!', fg='bright_green')


@cli.command(help='Update packages', group='Packages')
@click.argument('packages', nargs=-1, type=str)
@click.option('--refresh', help='Refresh Packages', default=True)
def update(packages, refresh):
    """Update a package"""
    if not packages:
        packages = ['all']

    if 'toaster' in packages or 'all' in packages:
        secho(
            ':: Updating toaster...', fg='bright_magenta')

        try:
            update_toaster()
        except NotFound:
            errecho(
                'Toaster source code is not in the standard location... you will need to manually update it!\n')
        else:
            secho('Toaster is now up to date! :)\n', fg='bright_green')

    # Update all
    if 'all' in packages:
        refresh_db()
        echo('')

        secho(
            ':: Updating packages...', fg='bright_magenta')

        try:
            update_all_packages()
        except AlreadyInstalled:
            pass

        secho('Packages are now up to date! :)\n', fg='bright_green')

        if platform.system() == 'Darwin':
            secho(
                ':: Checking for macOS updates...', fg='bright_magenta')

            c = sysupdates.check_updates()
            if c[0] != 0:
                errecho(
                    'An error has occured while checking for updates.')
                exit(1)

            if c[1]:
                secho('System updates available, starting updates!',
                      fg='bright_green')

                r = sysupdates.all()

                if r != 0:
                    errecho(
                        'An error has occured while updating your system.')
                    exit(1)
            else:
                secho('All up to date! :)\n', fg='bright_green')

        return

    # Update packages
    if refresh:
        refresh_db(auto=True)

    for package in packages:
        secho(
            f':: Installing {package}...', fg='bright_magenta')

        try:
            update_package(package)
        except NotFound:
            errecho(f'{package} is not installed.')
        except AlreadyInstalled:
            secho(
                f'{package} is already up to date :).', fg='bright_green')
        except NotImplementedError:
            errecho(
                f'{package} was found but is not available because it is a binary or app which is not supported yet.')
        else:
            secho(
                f'{package} updated!', fg='bright_green')


@cli.command(help='Link packages to your path', group='Packages')
@click.argument('packages', nargs=-1, type=str)
@click.option('--force/--no-force', help='Force packages to be linked', default=False)
def link(packages, force):
    for package in packages:
        secho(
            f':: Linking {package}...', fg='bright_magenta')

        try:
            package_toml = get_package_info(package, from_bakery=False)
            package_dir = get_package_loc(package)
        except NotFound:
            errecho(f'{package} is not installed.')
            return

        make_symlinks(package_toml, package_dir, force=force)

        secho(
            f'Linked {package}!', fg='bright_green')


@cli.command(help='Unlink packages from your path', group='Packages')
@click.argument('packages', nargs=-1, type=str)
def unlink(packages):
    for package in packages:
        secho(
            f':: Uninking {package}...', fg='bright_magenta')

        try:
            package_toml = get_package_info(package, from_bakery=False)
            package_dir = get_package_loc(package)
        except NotFound:
            errecho(f'{package} is not installed.')
            return

        remove_symlinks(package_toml, package_dir)

        secho(
            f'Unlinked {package}!', fg='bright_green')


if __name__ == '__main__':
    cli()
