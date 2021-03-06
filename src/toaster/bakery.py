from asyncore import write
import os
import json
import shutil
from atomicwrites import AtomicWriter
from git import Repo
import toml
from exceptions import AlreadyInstalled
from utils import CloneProgress, where_is_toaster, secho, errecho
from filelock import Timeout, SoftFileLock

toaster_loc = where_is_toaster()

db_lock_file = os.path.join(toaster_loc, 'bakery.json.lock')
db_lock = SoftFileLock(db_lock_file, timeout=1)


def check_lock():
    """Check if database file is locked"""
    try:
        db_lock.acquire()
    except:
        errecho(
            f'Unable to unlock database.\nIf you are sure another toaster process is not running, you can remove {db_lock_file}')
        exit(1)


def get_database():
    """Reads the database from file"""
    check_lock()

    with open(os.path.join(toaster_loc, 'bakery.json'), 'r') as f:
        return json.loads(f.read())


def write_database(db, release=True):
    """Overwrite the database with an updated one"""
    check_lock()

    with AtomicWriter(os.path.join(toaster_loc, 'bakery.json'), 'w', overwrite=True).open() as f:
        f.write(json.dumps(db))

    if release:
        # Release lock
        db_lock.release()


def add_bakery(name, loc):
    """Adds a bakery"""
    db = get_database()

    if name in db:
        secho(f'Bakery "{name}" exists, re-adding...', fg='yellow')

    db[name] = {}
    db[name]['repo'] = loc

    write_database(db)


def rm_bakery(name, loc):
    """Removes a bakery"""
    db = get_database()

    if not name in db:
        raise KeyError(name)

    del db[name]

    write_database(db)


def refresh_bakeries():
    """Refreshes all bakeries"""
    db = get_database()

    for bakery in db:
        git_url = db[bakery]['repo']
        repo_dir = os.path.join(toaster_loc, 'bakery', bakery)

        if os.path.exists(repo_dir):
            repo = Repo(repo_dir)
            repo.remotes.origin.pull()
        else:
            Repo.clone_from(git_url, repo_dir,
                            progress=CloneProgress(bakery, git_url))

        package_toml = toml.load(os.path.join(repo_dir, '_toaster.toml'))

        db[bakery]['name'] = package_toml['name']
        db[bakery]['maintainer'] = package_toml['maintainer']
        db[bakery]['description'] = package_toml['description']

        subfolders = [f.name for f in os.scandir(repo_dir) if f.is_dir()]

        packages = []

        for folder in subfolders:
            if not (folder.startswith('.')):
                packages.append(folder)

        db[bakery]['packages'] = packages

    write_database(db)


def get_all_packages():
    """Returns a list of all available packages"""
    db = get_database()
    pkgl = {}

    for bakery in db:
        pkgl[bakery] = db[bakery]['packages']

    return pkgl
