import bz2
import itertools
import os
import re
import subprocess
import sys
from typing import Generator, Iterable, Tuple

from humanize import naturalsize

__all__ = ['clean']

PKG_DB_FOLDER = '/var/db/pkg'


def load_files_from_manifest(manifest_file_name: str) -> list:
    print('Parse {}'.format(manifest_file_name))

    with open(manifest_file_name, 'r') as f:
        for line in (l for l in f if l.startswith('DIST') and l.count(' ') > 2):
            yield line.split(' ', 2)[1]


def load_files_from_manifests_folder(folder_name: str) -> list:
    print('Load manifests from {}'.format(folder_name))

    for root, _, files in os.walk(folder_name):
        for manifest in (name for name in files if name == 'Manifest'):
            for file_name in load_files_from_manifest(os.path.join(root, manifest)):
                yield file_name


def portage_env() -> list:
    if not hasattr(portage_env, 'cache'):
        portage_env.cache = subprocess.check_output(['emerge', '--info']).decode('utf-8').split('\n')
    return portage_env.cache


def extract_path(line: str) -> list:
    return line.strip('"').split(' ')


def emerge_value(key: str) -> str:
    try:
        return next(l.split('=')[1] for l in portage_env() if l.startswith('{}='.format(key)))
    except StopIteration:
        return str()


def manifests_folders() -> Generator[str, None, None]:
    regex = re.compile(r' *location: (.*)')
    matches = (regex.match(e) for e in portage_env())
    return (m.group(1) for m in matches if m)


def load_file_names() -> list:
    for folder_name in manifests_folders():
        for file_name in load_files_from_manifests_folder(folder_name):
            yield file_name


def distdir() -> str:
    return extract_path(emerge_value('DISTDIR'))[0]


def parse_env_file(file_name: str) -> Iterable[str]:
    print('Parse {}'.format(file_name))
    name_re = re.compile(r'declare -x A+="(.*)"')
    with bz2.BZ2File(file_name, 'r') as f:
        matches = (name_re.match(l.decode('utf-8')) for l in f.readlines())
        return itertools.chain(*[m.group(1).split(' ') for m in matches if m])


def installed_files() -> Generator[None, str, None]:
    for dir_path, _, _ in os.walk(PKG_DB_FOLDER):
        env_file = os.path.join(dir_path, 'environment.bz2')
        if os.path.exists(env_file):
            yield from parse_env_file(env_file)


def files_for_clean(not_installed: bool) -> Generator[None, Tuple[str, int], None]:
    file_names = set(installed_files() if not_installed else load_file_names())
    distdir_path = distdir()

    for file_name in (f for f in os.listdir(distdir_path) if f not in file_names):
        full_entry_name = os.path.join(distdir_path, file_name)
        if os.path.isfile(full_entry_name):
            yield full_entry_name, os.path.getsize(full_entry_name)


def human_size(size):
    return naturalsize(size, '%.2f')


def clean():
    can_remove = sys.argv.count('--rm')
    not_installed = sys.argv.count('--not-installed')

    total_size = 0
    removed_size = 0
    for file_path, file_size in files_for_clean(not_installed):
        print('[ {:>10} ] {}'.format(human_size(file_size), file_path))
        total_size += file_size
        if can_remove:
            try:
                os.remove(file_path)
                removed_size += file_size
            except Exception as e:
                print(e)

    print('=' * 120)
    print('[ {:>10} ] Total size'.format(human_size(total_size)))
    print('[ {:>10} ] Removed size'.format(human_size(removed_size)))


if __name__ == '__main__':
    clean()
