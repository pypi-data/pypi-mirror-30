import os
from glob import glob
from contextlib import contextmanager


@contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


def write_generated_file(path, source):
    dirname = os.path.dirname(path)

    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)

    with open(path, 'w') as f:
        f.write(source)


def copy_generated_tree(source_path, target_path, glob_expr="**/*"):
    files = []

    with chdir(source_path):
        for file in glob(glob_expr, recursive=True):
            with open(file, 'r') as f:
                files.append((file, f.read()))

    with chdir(target_path):
        for path, source in files:
            write_generated_file(path, source)


def extract_files(dst, files):
    for rq_file in files:
        full_path = os.path.join(dst, rq_file['name'])

        write_generated_file(full_path, rq_file['body'])


def collect_files(src):
    with chdir(src):
        paths = []
        paths += list(glob('*.col'))
        paths += list(glob('col/**/*.col', recursive=True))
        files = {}
        for path in set(paths):
            with open(path, 'r') as f:
                files[path] = f.read()
    return files
