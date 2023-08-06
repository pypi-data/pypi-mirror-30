import os
import re
from glob import glob
from contextlib import contextmanager
import subprocess


@contextmanager
def chdir(path):
    cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(cwd)


def write_generated_file(path, source):
    dirname = os.path.dirname(path)
    if dirname and len(dirname) and not os.path.exists(dirname):
        os.makedirs(dirname)

    if os.path.exists(path):
        with open(path, 'r') as f:
            if path.endswith('.py'):
                match = re.match('^\s*#\s*freeze(\s*,\s+generate\s+to\s*:\s*([a-zA-Z0-9\.\-_]+.py))?', f.read(100))
                if match:
                    print('NB! Skipping file {} as it contains #freeze marker'.format(path))
                    if match.group(2):
                        print('NB! Generating to {} instead'.format(match.group(2)))
                        path = os.path.join(os.path.dirname(path), match.group(2))
                    else:
                        return
            else:
                if not re.match('^\s*{#\s*generated\s*#}\s*', f.read(20)):
                    return

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


def collect_app_names():
    collections = []
    for filename in os.listdir('.'):
        if os.path.isfile(filename) and filename.endswith('.col'):
            if not re.match('^[a-zA-Z][a-zA-Z0-9_]+\.col$', filename):
                print('Collection file has incorrect name: {}'.format(filename))
            app_name = filename[0:-4]
            collections.append(app_name)
    return collections


def migrate_db(apps, features=None):
    if not features:
        features = []
    else:
        features = features.split(',')

    is_cratis = features and 'cratis' in features

    if is_cratis:
        django_command = 'django'
    else:
        django_command = 'python manage.py'

    for app_name in apps:
        subprocess.run('{} makemigrations {}'.format(django_command, app_name), shell=True, check=True)
        try:
            subprocess.run('{} migrate {}'.format(django_command, app_name), shell=True, check=True)
        except subprocess.CalledProcessError:
            pass

        if is_cratis:
            subprocess.run('{} sync_translation_fields_safe'.format(django_command), shell=True, check=True)


def install_deps():
    subprocess.run('pip install -r requirements.txt', shell=True, check=True)
