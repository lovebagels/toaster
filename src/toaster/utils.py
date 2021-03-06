import hashlib
import os
import platform
import shutil
from pathlib import Path

import requests
from click import echo
from click import secho
from exceptions import NotFound
from git import RemoteProgress
from git import Repo
from tqdm.auto import tqdm


def where_is_toaster():
    """Returns the directory toaster is installed in"""
    return os.path.join(str(Path.home()), '.toaster')


def errecho(err, **kwargs):
    """Echo an error message"""
    secho(err, fg='bright_red', **kwargs)


def download_file(url, loc):
    """Download a file"""
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))

        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
            with open(loc, 'wb') as output:
                shutil.copyfileobj(raw, output)


def verify_file(file, hash):
    """Verifies files using an sha256 hash."""
    with open(file, "rb") as f:
        file_hash = hashlib.sha256()
        chunk = f.read(4096)

        while chunk:
            file_hash.update(chunk)
            chunk = f.read(4096)

    if file_hash.hexdigest() == hash:
        return True

    return False


def _get_val_for_sys(d, item, system):
    i = None

    if item in d[system]:
        i = d[system]
    elif type(d[system]) is list:
        if len(d[system]) > 0:
            i = d[system][0]

    if i:
        if item in i:
            return i[item]


def dependingonsys(d, item, append_mode=False):
    """Get platform-specific values from a dict"""
    if append_mode:
        res = []
    else:
        res = None

    if item in d:
        if append_mode:
            res += d[item]
        else:
            res = d[item]

    if platform.system() != 'Darwin':
        if 'linux_any' in d:
            ans = _get_val_for_sys(d, item, 'linux_any')

            if ans:
                if append_mode:
                    res += ans
                else:
                    res = ans

        if not (platform.machine().startswith('arm') or platform.machine().startswith('aarch')):
            if 'linux_x86_64' in d:
                ans = _get_val_for_sys(d, item, 'linux_x86_64')

                if ans:
                    if append_mode:
                        res += ans
                    else:
                        res = ans
    elif platform.system() == 'Darwin':
        if 'universal' in d:
            ans = _get_val_for_sys(d, item, 'universal')

            if ans:
                if append_mode:
                    res += ans
                else:
                    res = ans

        if platform.machine() == 'arm64':
            if 'arm64' in d:
                ans = _get_val_for_sys(d, item, 'arm64')

                if ans:
                    if append_mode:
                        res += ans
                    else:
                        res = ans
        else:
            if 'x86_64' in d:
                ans = _get_val_for_sys(d, item, 'x86_64')

                if ans:
                    if append_mode:
                        res += ans
                    else:
                        res = ans

    return res


def update_toaster():
    toaster_src_dir = os.path.join(where_is_toaster(), 'toaster')

    if not os.path.exists(toaster_src_dir):
        raise NotFound('toaster source')

    repo = Repo(toaster_src_dir)
    repo.remotes.origin.pull()


class CloneProgress(RemoteProgress):
    """Progress bar for git cloning"""

    def __init__(self, package, url):
        super().__init__()
        self.pbar = tqdm(desc=f'Cloning {url}...')

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()
