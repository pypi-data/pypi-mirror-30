import click
import get as get_package
import put as put_package
import watch as watch_package
import utils


@click.group()
def get_group():
    pass


@get_group.command()
@click.argument('key', required=True)
@click.argument('path', required=True)
@click.option('--code/--no-code', default=True, help='get code source')
@click.option('--result/--no-result', default=True, help='get result')
def get(key, path, code, result):
    if code:
        get_package.Get(key).get(path)
    if result:
        get_package.Get(key, 'result').get(path)


@click.group()
def put_group():
    pass


@put_group.command()
@click.argument('key', required=True)
@click.argument('path', required=True)
@click.option('--folder/--no-folder', default=True, help='upload directory')
@click.option('--code/--no-code', default=False, help='upload code')
@click.option('--result/--no-result', default=False, help='put result')
def put(key, path, folder, code, result):
    if code:
        put_package.Put(key).put(path, folder)
    if result:
        put_package.Put(key, 'result').put(path, folder)


@click.group()
def watch_group():
    pass


@watch_group.command()
@click.option('-t', '--time', default=10, help='loop time (s)')
def watch(time):
    watch_package.Watch(time).watch()


@click.group()
def init_group():
    pass


@init_group.command()
def init():
    utils.init_environment()


cli = click.CommandCollection(sources=[get_group, put_group, watch_group, init_group])


def main():
    cli()


if __name__ == "__main__":
    cli()
