from click import echo, secho
import os
import hashlib
import requests
import shutil
from tqdm.auto import tqdm
from git import RemoteProgress, Repo


def errecho(err, **kwargs):
    secho(err, fg='bright_red', **kwargs)


def download_file(url):
    # make an HTTP request within a context manager
    with requests.get(url, stream=True) as r:
        total_length = int(r.headers.get("Content-Length"))

        with tqdm.wrapattr(r.raw, "read", total=total_length, desc="")as raw:
            with open(f"{os.path.basename(r.url)}", 'wb')as output:
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


class CloneProgress(RemoteProgress):
    def __init__(self, package, url):
        super().__init__()
        self.pbar = tqdm(desc=f'Cloning {url}...')

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()
