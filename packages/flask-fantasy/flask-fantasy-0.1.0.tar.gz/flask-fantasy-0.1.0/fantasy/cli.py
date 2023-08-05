"""
=============
CLI工具包
=============
"""

import importlib
import os
import shutil
import sys

import click
from flask import current_app as app
from flask.cli import with_appcontext


@click.group()
def ff():
    """
    Fantasy tool-box
    """
    pass


@ff.command()
@click.option('--migrations-root', type=click.Path(exists=False))
@with_appcontext
def makemigrations(migrations_root):
    """等价于 django makemigrations 操作"""
    from flask_migrate import (Migrate, init as migrate_init,
                               migrate as migrate_exec)

    migrations_root = migrations_root or os.path.join(
        os.environ.get('FANTASY_MIGRATION_PATH',
                       os.getcwd()),
        'migrations')

    migrations_root = os.path.expanduser(migrations_root)

    mig = Migrate(app, app.db, directory=migrations_root)

    if not os.path.exists(migrations_root):
        migrate_init(migrations_root)
        pass

    models_file = os.path.join(migrations_root, 'models.txt')

    if not os.path.exists(models_file):
        with open(models_file, 'w') as fw:
            fw.write('\0')
            pass
        pass

    with open(models_file, 'r') as fp:
        modules = fp.readlines()
        pass

    modules = filter(lambda x: x.strip("\n"), modules)
    modules = map(lambda x: x.strip("\n").split("#")[0].strip(), modules)

    for m in modules:
        importlib.import_module(m + '.models')
        pass

    migrate_exec(migrations_root)
    mig.init_app(app, app.db)
    pass


@ff.command()
@click.option('--migrations-root', type=click.Path(exists=False))
@with_appcontext
def migrate(migrations_root):
    """等价于 django migrate 操作"""
    from flask_migrate import Migrate, upgrade as migrate_upgrade
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.engine.url import make_url
    from sqlalchemy_utils import database_exists, create_database

    db = SQLAlchemy()
    dsn = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
    if not database_exists(dsn):
        create_database(dsn)
        pass

    migrations_root = migrations_root or os.path.join(
        os.environ.get('FANTASY_MIGRATION_PATH',
                       os.getcwd()),
        'migrations')
    migrations_root = os.path.expanduser(migrations_root)

    if os.path.exists(migrations_root):
        mig = Migrate(app, db, directory=migrations_root)
        mig.init_app(app, db)
        migrate_upgrade(migrations_root)
    else:
        click.echo(
            click.style('migration files not exist,skip migrate...', fg='red'))
        sys.exit(-1)
    pass


@ff.command()
@click.option('--work-dir', type=click.Path(exists=False))
@click.option('--hive-root', type=click.Path(exists=True),
              default=os.path.expanduser('~/Codes/1024/hive/'))
@click.option('--active-module', '-a',
              multiple=True, help='load order will effect generate file')
@with_appcontext
def requirements(work_dir, hive_root, active_module):
    """编译全新依赖文件"""
    import fileinput

    work_dir = work_dir or os.path.join(
        os.environ.get('FANTASY_APP_PATH',
                       os.getcwd()))

    work_dir = os.path.expanduser(work_dir)

    requirements_root = os.path.join(work_dir, 'requirements')
    migrate_root = os.path.join(work_dir, 'migrations')

    if not os.path.exists(requirements_root):
        os.makedirs(requirements_root)
        pass

    click.echo(click.style("Generate hive requirements...", fg="yellow"))

    shutil.copy(
        os.path.join(hive_root, 'requirements.txt'),
        os.path.join(requirements_root, 'hive.txt')
    )

    click.echo(click.style("Generate hive-module requirements...",
                           fg="yellow"))

    active_module = set(active_module)
    active_module = sorted(list(active_module))

    possible = set()

    for m in active_module:
        for i in range(m.count('.') + 1):
            possible.add(m.rsplit('.', i)[0].replace('.', '/'))
            pass

        pass

    possible = sorted(list(possible))

    requirements_files = filter(
        lambda x: os.path.exists(x),
        map(lambda x: os.path.join(hive_root,
                                   x, 'requirements.txt'), possible))

    module_packages = set()
    with fileinput.input(requirements_files) as fp:
        for line in fp:
            pkg = line.split('#')[0].strip()
            if pkg:
                module_packages.add(pkg)
        pass

    with click.open_file(os.path.join(requirements_root, 'hive-modules.txt'),
                         'w') as fp:
        for p in module_packages:
            fp.write("%s\n" % p)
        pass

    path_module = map(lambda x: x.replace('.', '/'), active_module)

    modules_path = ' '.join(path_module)

    docker_file = os.path.join(
        os.path.dirname(requirements_root),
        'Dockerfile'
    )

    if os.path.exists(docker_file):
        click.echo(click.style("Found Dockerfile,try update...",
                               fg="yellow"))

        with open(docker_file, 'r') as fp:
            buffer = fp.read()
            pass
        import re
        replaced = re.sub('ARG ACTIVE_PACKAGES=".*"',
                          'ARG ACTIVE_PACKAGES="%s"' % modules_path,
                          buffer)
        with open(docker_file, 'w') as fp:
            fp.write(replaced)
            pass

        pass

    if os.path.exists(migrate_root):

        models_files = filter(
            lambda x: os.path.exists(x),
            map(lambda x: os.path.join(hive_root,
                                       x, 'models.py'), possible))

        models = map(
            lambda x: x.replace(
                hive_root, '').replace('/models.py',
                                       '').replace('/',
                                                   '.'),
            models_files)

        click.echo(click.style("Found models.txt,try update...",
                               fg="yellow"))
        with open(os.path.join(migrate_root, 'models.txt'), 'w') as fp:
            for p in models:
                fp.write("%s\n" % p)
            pass
        pass


    if os.path.exists(migrate_root):

        tasks_files = filter(
            lambda x: os.path.exists(x),
            map(lambda x: os.path.join(hive_root,
                                       x, 'tasks.py'), possible))

        tasks = map(
            lambda x: x.replace(
                hive_root, '').replace('/tasks.py',
                                       '').replace('/',
                                                   '.'),
            tasks_files)

        click.echo(click.style("Found tasks.txt,try update...",
                               fg="yellow"))
        with open(os.path.join(migrate_root, 'tasks.txt'), 'w') as fp:
            for p in tasks:
                fp.write("%s\n" % p)
            pass
        pass


    click.echo(click.style("Generate done...", fg="yellow"))
    pass


@ff.command()
@click.option('--celery-arguments', '-a', type=click.STRING,
              help='celery worker command arguments')
@with_appcontext
def queue(celery_arguments):
    """启动队列服务[开发中]"""

    if not app.celery:
        return click.echo(
            click.style('No celery config found，skip start...', fg='yellow'))

    celery = app.celery
    celery.autodiscover_tasks()

    argv = celery_arguments.split()
    argv.insert(0, 'worker')
    argv.insert(0, 'Queue')
    celery.worker_main(argv)
    pass
