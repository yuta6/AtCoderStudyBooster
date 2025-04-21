from importlib.metadata import metadata

import rich_click as click
from click_aliases import ClickAliasedGroup
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.traceback import install
from rich_click import RichGroup

from atcdr.download import download
from atcdr.generate import generate
from atcdr.login import login
from atcdr.logout import logout
from atcdr.markdown import markdown
from atcdr.open import open_files
from atcdr.submit import submit
from atcdr.test import test


# ─── RichClick + ClickAliases 両対応の Group クラス ───
class AliasedRichGroup(ClickAliasedGroup, RichGroup):
    def format_commands(self, ctx, console, *args, **kwargs):
        console = Console()
        commands = self.list_commands(ctx)

        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column('command', style='bold cyan', no_wrap=True)
        table.add_column('help', style='')

        for name in commands:
            cmd = self.get_command(ctx, name)
            if not cmd or getattr(cmd, 'hidden', False):
                continue

            aliases = self._commands.get(name, [])
            alias_part = f"[dim]({', '.join(aliases)})[/]" if aliases else ''

            short = (
                cmd.get_short_help_str()
                if hasattr(cmd, 'get_short_help_str')
                else cmd.short_help or ''
            )
            table.add_row(f'{name}{alias_part}', short)

        panel = Panel(table, title='Commands', expand=False)
        console.print(panel)


# ─── CLI 定義 ──────────────────────────────────────────
_meta = metadata('AtCoderStudyBooster')
_NAME = _meta['Name']
_VERSION = _meta['Version']

click.rich_click.MAX_WIDTH = 100
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.STYLE_HELPTEXT_FIRST_LINE = 'bold cyan'
click.rich_click.STYLE_HELPTEXT = 'dim'


@click.group(
    cls=AliasedRichGroup,
    context_settings={'help_option_names': ['-h', '--help']},
)
@click.version_option(
    _VERSION,
    '-v',
    '--version',
    prog_name=_NAME,
    message='%(prog)s %(version)s',
)
def cli():
    install()


cli.add_command(test, aliases=['t'])
cli.add_command(download, aliases=['d'])
cli.add_command(open_files, 'open', aliases=['o'])
cli.add_command(generate, aliases=['g'])
cli.add_command(markdown, aliases=['md'])
cli.add_command(submit, aliases=['s'])
cli.add_command(login)
cli.add_command(logout)

if __name__ == '__main__':
    cli()
