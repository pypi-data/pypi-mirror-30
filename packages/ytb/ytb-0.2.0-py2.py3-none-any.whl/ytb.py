import re
import subprocess

import click


def _format_url(url):
    return re.sub(r'\\', '', url)


def _run_cmd(cmd):
    print(cmd)
    cmd = cmd.split(' ')
    result = subprocess.run(
        cmd, stdout=subprocess.PIPE)
    print(result.stdout.decode('utf-8'))


@click.group()
def cli():
    pass


@cli.command()
def init():
    _run_cmd("brew install youtube-dl")


@cli.command()
@click.argument("url")
def show(url):
    url = _format_url(url)
    cmd = ('youtube-dl --proxy=127.0.0.1:8090'
           ' --list-formats {url}').format(url=url)
    _run_cmd(cmd)


@cli.command()
@click.option("-f", "--format", help="format to use")
@click.argument("url")
def down(format, url):
    url = _format_url(url)
    cmd = ('youtube-dl --proxy=127.0.0.1:8090'
           ' -c -k --write-auto-sub --convert-subs'
           ' ass -f {format} {url}').format(url=url, format=format)
    _run_cmd(cmd)


if __name__ == "__main__":
    cli()
