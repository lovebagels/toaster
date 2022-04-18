import os
import json
from atomicwrites import AtomicWriter
from git import Repo
import toml
from utils import CloneProgress


def get_database():
    with open(f'/opt/toaster/bakery.json', 'r') as f:
        return json.loads(f.read())


def refresh_bakeries():
    db = get_database()

    for bakery in db:
        git_url = db[bakery]['repo']
        repo_dir = os.path.join('/opt/toaster/bakery', bakery)

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

    with AtomicWriter('/opt/toaster/bakery.json', 'w', overwrite=True).open() as f:
        f.write(json.dumps(db))


def get_all_packages():
    db = get_database()
    pkgl = {}

    for bakery in db:
        pkgl[bakery] = db[bakery]['packages']

    return pkgl
