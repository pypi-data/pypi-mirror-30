import os
import sys

import click

from genius_cli.client import GeniusClient
from genius_cli.utils import collect_files, extract_files, collect_app_names, migrate_db, install_deps


def run():
    api_token = os.environ.get('GENIUS_TOKEN', None)
    features_env = os.environ.get('GENIUS_FEATURES', None)

    if not api_token:
        print('No genius api token. Add GENIUS_TOKEN variable to your profile.')
        sys.exit(1)

    genius = GeniusClient(
        api_url=os.environ.get('GENIUS_URL', 'https://genius-project.io/en/api/'),
        token=api_token,
    )

    @click.group()
    def cli():
        pass

    @click.command()
    @click.option('--auto', is_flag=True, help='Generate and run migrations')
    # @click.option('--install', is_flag=True, help='Install dependencies')
    @click.option('--src', default='.', help='Sources path')
    @click.option('--dst', default='.', help='Target path')
    @click.option('--name', help='Request name (for debug purposes)')
    @click.option('--with', default='', help='Extra features to use (coma separated)')
    @click.argument('app', nargs=-1)
    def gen(auto, src, dst, name, app, **kwargs):
        if len(app) == 0:
            app = collect_app_names()

        src = os.path.realpath(src)
        dst = os.path.realpath(dst)

        files = collect_files(src)

        features = kwargs.get('with', features_env)
        data = genius.generate(files, name=name, collections=app, features=features)

        extract_files(dst, data['response']['files'])

        if auto:
            # install_deps()
            migrate_db(apps=app, features=features)

    gen()


