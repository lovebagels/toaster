#!/usr/bin/env python3
import sys
from exceptions import *
from urllib.parse import urlparse

import validators

import click
from click_aliases import ClickAliasedGroup

import sysupdates
from utils import errecho, echo, secho
from packages import install_package, remove_package, update_package
from bakery import refresh_bakeries, add_bakery, rm_bakery


# https://stackoverflow.com/a/58770064
class GroupedGroup(ClickAliasedGroup):
    def command(self, *args, **kwargs):
        """Gather the command help groups"""
        help_group = kwargs.pop('group', None)
        decorator = super(GroupedGroup, self).command(*args, **kwargs)

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
    """Refresh database"""
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
    refresh_db()


@cli.command(help='Add bakeries', group='Bakeries')
@click.argument('bakeries', nargs=-1, required=True, type=str)
def bakery(bakeries):
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


@cli.command(help='Install packages', group='Packages')
@click.argument('packages', nargs=-1, required=True, type=str)
@click.option('--refresh', help='Refresh Packages', default=True, type=bool)
def install(packages, refresh):

    for package in packages:
        if refresh:
            refresh_db(auto=True)

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
        else:
            secho(
                f'{package} installed!', fg='bright_green')


@cli.command(help='Remove packages', aliases=['uninstall'], group='Packages')
@click.argument('packages', nargs=-1, required=True, type=str)
def remove(packages):
    for package in packages:
        secho(
            f':: Remoivng {package}...', fg='bright_magenta')
        try:
            remove_package(package)
        except NotFound:
            success = False
            return errecho(f'{package} is not installed.')

        secho(
            f'Removed {package}!', fg='bright_green')


@cli.command(help='Update packages', group='Packages')
@click.argument('packages', nargs=-1, type=str)
@click.option('--refresh', help='Refresh Packages', default=True, type=bool)
def update(packages, refresh):

    if not packages:
        packages = ['all']

    if 'all' in packages:
        refresh_db()

        secho(
            ':: Updating packages...', fg='bright_magenta')

        secho(
            ':: Checking for macOS updates...', fg='bright_magenta')

        c = sysupdates.check_updates()
        if c[0] != 0:
            errecho(
                'An error has occured while checking for updates.')
            exit(1)

        if c[1]:
            secho(':: System updates available, starting updates!',
                  fg='bright_magenta')

            r = sysupdates.all()

            if r != 0:
                errecho(
                    'An error has occured while updating your system.')
                exit(1)
        else:
            secho('All up to date! :)', fg='bright_green')

        return

    for package in packages:
        if refresh:
            refresh_db(auto=True)

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


def main():
    cli()


if __name__ == '__main__':
    main()
