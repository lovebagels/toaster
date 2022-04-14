import subprocess


def check_updates():
    """Checks if any updates are available, returns a return code and list of updates"""
    p = subprocess.Popen(
        ['softwareupdate', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = p.communicate()

    updates = []

    if p.returncode == 0:
        for line in out.decode().split('\n'):
            line = line.strip()

            if line.startswith('*'):
                updates.append(line.lstrip(" *").rstrip(" -"))

    return p.returncode, updates


def all():
    """Downloads and installs all available updates"""
    p = subprocess.run(
        ['softwareupdate', '-ai'])

    return p.returncode
