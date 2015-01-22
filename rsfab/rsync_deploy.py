"""
    Rsync helper functions
"""
from datetime import datetime
import os

from fabric.api import env, local
from fabric.context_managers import lcd
from fabric.contrib.project import rsync_project


def rsync_update_project():
    rsync_project(
        remote_dir=env.project_path,
        local_dir=env.rsync_local,
        exclude=env.rsync_exclude,
        delete=env.rsync_delete
    )


def setup_rsync(rsync_exclude, rsync_local, rsync_delete=False):
    """
        setup all needed vars
    """

    env.rsync_exclude = rsync_exclude
    env.rsync_local = rsync_local
    env.rsync_delete = rsync_delete


def rsync_update_from_git():
    """
        Update project via rsync based on settings from \
        rsync_deploy.setup_rsync(), git_deploy.setup_git() \
        and project.setup_project_path()
    """

    if not env.get('git_url'):
        raise AssertionError('Please set env.git_url.')

    # create a temporary directory name
    tmp_dir = datetime.utcnow().strftime('%Y%m%d%H%M%S')

    # the code below really should be in a well-grained try-except block
    # to cleanup tmp_dir directory

    # and clone to it
    local('git clone %(git_url)s .{0}'.format(tmp_dir) % env)

    # do branch switching and pull changes from it, if needed
    with lcd('.{0}'.format(tmp_dir)):
        if env.get('git_branch'):
            local('git checkout %(git_branch)s' % env)
        elif env.get('git_tag'):
            local('git checkout %(git_tag)s' % env)
        local('git pull')

    # do rsync
    _old_local = env.rsync_local
    env.rsync_local = os.path.join('.{0}'.format(tmp_dir), '*')
    rsync_update_project()
    env.rsync_local = _old_local

    # cleanup the temporary dir
    local('rm -rf .{0}'.format(tmp_dir))
