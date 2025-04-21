from importlib.metadata import metadata

import rich_click as click
from click_aliases import ClickAliasedGroup
from rich.traceback import install

from atcdr.download import download
from atcdr.generate import generate
from atcdr.login import login
from atcdr.logout import logout
from atcdr.markdown import markdown
from atcdr.open import open_files
from atcdr.submit import submit
from atcdr.test import test

# パッケージメタデータ取得
_meta = metadata('AtCoderStudyBooster')
_NAME = _meta['Name']
_VERSION = _meta['Version']


@click.group(cls=ClickAliasedGroup)
@click.version_option(
    _VERSION, '-v', '--version', prog_name=_NAME, message='%(prog)s %(version)s'
)
def cli():
    install()


cli.add_command(test, name='test', aliases=['t'])
cli.add_command(download, name='download', aliases=['d'])
cli.add_command(open_files, name='open', aliases=['o'])
cli.add_command(generate, name='generate', aliases=['g'])
cli.add_command(markdown, name='markdown', aliases=['md'])
cli.add_command(login, name='login')
cli.add_command(logout, name='logout')
cli.add_command(submit, name='submit', aliases=['s'])

if __name__ == '__main__':
    cli()
