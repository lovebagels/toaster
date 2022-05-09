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


@click.group(cls=ClickAliasedGroup)
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


@cli.command(help='Add bakeries')
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


@cli.command(help='Remove bakeries')
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


@cli.command(help='Install packages')
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


@cli.command(help='Remove packages', aliases=['uninstall'])
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


@cli.command(help='Update packages')
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
    cli.add_command(update)
    cli.add_command(install)
    cli.add_command(remove)
    cli.add_command(bakery)
    cli()


if __name__ == '__main__':
    main()
