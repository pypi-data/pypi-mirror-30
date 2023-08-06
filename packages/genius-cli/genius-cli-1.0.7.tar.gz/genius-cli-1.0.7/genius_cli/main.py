import os
import tempfile

import click
import sys

from genius_cli.client import GeniusClient
from genius_cli.utils import collect_files, extract_files, chdir, copy_generated_tree


def run():
    api_token = os.environ.get('GENIUS_TOKEN', None)
    if not api_token:
        print('No genius api token. Add GENIUS_TOKEN variable to your profile.')
        sys.exit(1)

    genius = GeniusClient(
        api_url=os.environ.get('GENIUS_URL', 'http://genius-project.io/en/api/'),
        token=api_token,
    )

    @click.group()
    def cli():
        pass

    @click.command()
    @click.option('--auto', is_flag=True, help='Generate and run migrations')
    @click.option('--src', default='.', help='Sources path')
    @click.option('--dst', default='.', help='Target path')
    @click.option('--name', help='Request name (for debug purposes)')
    @click.argument('app', nargs=-1)
    def gen(auto, src, dst, name, app, **kwargs):
        if len(app) == 0:
            print('Please specify application name')
            return

        src = os.path.realpath(src)
        dst = os.path.realpath(dst)

        files = collect_files(src)

        data = genius.generate(files, name=name, collections=app)

        extract_files(dst, data['response']['files'])

    # @click.command()
    # def up():
    #     with tempfile.TemporaryDirectory() as tmp_path:
    #         with chdir(tmp_path):
    #             os.system('django-admin startproject app')
    #         copy_generated_tree(os.path.join(tmp_path, 'app'), os.getcwd(), '**/*.py')

    # cli.add_command(gen)
    # cli.add_command(up)

    gen()


