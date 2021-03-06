"""
Deploy reps.mozilla.org using Chief in dev/stage/production.

Requires commander_ which is installed on the systems that need it.

.. _commander: https://github.com/oremj/commander
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from commander.deploy import task, hostgroups
import commander_settings as settings


@task
def update_code(ctx, tag):
    """Update the code to a specific git reference (tag/sha/etc)."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('git fetch')
        ctx.local('git checkout -f %s' % tag)
        ctx.local('git submodule sync')
        ctx.local('git submodule update --init --recursive')


@task
def update_assets(ctx):
    with ctx.lcd(settings.SRC_DIR):
        # LANG=en_US.UTF-8 is sometimes necessary for the YUICompressor.
        ctx.local('LANG=en_US.UTF8 python ./manage.py collectstatic --noinput')
        ctx.local('LANG=en_US.UTF8 python ./manage.py compress_assets')


@task
def update_db(ctx):
    """Update the database schema, if necessary.

    """
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('python ./manage.py migrate')

@task
def update_product_details(ctx):
    """Update the product details

    """
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('python ./manage.py update_product_details ')


@task
def checkin_changes(ctx):
    """Use the local, IT-written deploy script to check in changes."""
    ctx.local(settings.DEPLOY_SCRIPT)


@hostgroups(settings.WEB_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def deploy_app(ctx):
    """Call the remote update script to push changes to webheads."""
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)
    ctx.remote('/bin/touch %s' % settings.REMOTE_WSGI)


@hostgroups(settings.CELERY_HOSTGROUP, remote_kwargs={'ssh_key': settings.SSH_KEY})
def update_celery(ctx):
    """Update and restart Celery."""
    ctx.remote(settings.REMOTE_UPDATE_SCRIPT)
    ctx.remote('/sbin/service %s restart' % settings.CELERY_SERVICE)


@task
def update_info(ctx):
    """Write info about the current state to a publicly visible file."""
    with ctx.lcd(settings.SRC_DIR):
        ctx.local('date > media/revision_info.txt')
        ctx.local('git branch >> media/revision_info.txt')
        ctx.local('git log -3 >> media/revision_info.txt')
        ctx.local('git status >> media/revision_info.txt')
        ctx.local('git submodule status >> media/revision_info.txt')
        ctx.local('git rev-parse HEAD > media/revision.txt')


@task
def pre_update(ctx, ref=settings.UPDATE_REF):
    """Update code to pick up changes to this file."""
    update_code(ref)
    update_info()


@task
def update(ctx):
    update_assets()
    update_db()


@task
def deploy(ctx):
    checkin_changes()
    deploy_app()
    update_celery()


@task
def update_site(ctx, tag):
    """Update the app to prep for deployment."""
    pre_update(tag)
    update()
