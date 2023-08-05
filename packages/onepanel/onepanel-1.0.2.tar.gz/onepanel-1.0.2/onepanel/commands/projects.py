""" Command line interface for the OnePanel Machine Learning platform

'Projects' commands group.
"""

import os
import configobj
import json
import re
import click
from prettytable import PrettyTable
from onepanel.commands.login import login_required
from onepanel.gitwrapper import GitWrapper


class Project:
    """ Projects data model
    """

    PROJECT_FILE = '.onepanel/project'
    EXCLUSIONS = ['.onepanel/project']

    def __init__(self, account_uid=None, project_uid=None):
        self.account_uid = account_uid
        self.project_uid = project_uid        

    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        project_file = os.path.join(home, Project.PROJECT_FILE)

        cfg = configobj.ConfigObj(project_file)
        cfg['uid'] = self.project_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    @classmethod
    def from_json(cls, data):
        project = cls(data['account']['uid'], data['uid'])
        return project

    @classmethod
    def from_directory(cls, home):
        if not Project.exists_local(home):
            return None

        project_file = os.path.join(home, Project.PROJECT_FILE)
        cfg = configobj.ConfigObj(project_file)
        project = cls(cfg['account_uid'], cfg['uid'])
        return project

    @staticmethod
    def is_uid_valid(uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @staticmethod
    def exists_local(home):
        project_file = os.path.join(home, Project.PROJECT_FILE)
        if os.path.isfile(project_file):
            return True
        else:
            return False

    @staticmethod
    def exists_remote(project_uid, data):
        exists = False
        if data['uid'] == project_uid:
            exists = True
        return exists

    @staticmethod
    def print_list(data):
        if len(data) == 0:
            print('No projects found')
            return

        tbl = PrettyTable(border=False)
        tbl.field_names = ['NAME', 'INSTANCES', 'JOBS']
        tbl.align = 'l'
        for row in data:
            tbl.add_row([row['uid'], row['instanceCount'], row['jobCount']])
        print(tbl)


def create_project(ctx, account_uid, home):
    """ Project creation method for 'projects_init' and 'projects_create'
    commands
    """

    conn = ctx.obj['connection']

    if not account_uid:
        account_uid = conn.account_uid

    project_uid = os.path.basename(home)
    if not Project.is_uid_valid(project_uid):
        click.echo('Project name {} is invalid.'.format(project_uid))
        click.echo('Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        return None

    r = conn.get('{}/accounts/{}/projects/{}'.format(conn.URL, account_uid, project_uid))
    if r.status_code == 200:
        remote_project = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return None

    project = None
    if Project.exists_remote(project_uid, remote_project):
        if Project.exists_local(home):
            click.echo('Project is already initialized')
        else:
            project = Project(account_uid, project_uid)
            project.save(home)
            git = GitWrapper()
            git.init(home, account_uid, project_uid)
            git.exclude(home, Project.EXCLUSIONS)

    else:
        can_create = True
        if Project.exists_local(home):
            can_create = click.confirm(
                'Project exists locally but does not exist in {}, create the project and remap local folder?'
                .format(account_uid))

        if can_create:
            url = '{}/accounts/{}/projects'.format(conn.URL, account_uid)
            data = {
                'uid': project_uid
            }
            r = conn.post(url, data=json.dumps(data))

            if r.status_code == 200:
                project = Project.from_json(r.json())
                project.save(home)
                git = GitWrapper()
                git.init(home, account_uid, project_uid)
                git.exclude(home, Project.EXCLUSIONS)
            else:
                print('Error: {}'.format(r.status_code))

    return project

@click.group(help='Project commands group')
@click.pass_context
def projects(ctx):
    pass


@projects.command('list', help='Display a list of all projects.')
@click.pass_context
@login_required
def projects_list(ctx):
    conn = ctx.obj['connection']
    url = '{}/projects'.format(conn.URL)

    r = conn.get(url)
    if r.status_code == 200:
        Project.print_list(r.json())
    elif r.status_code == 404:
        print('No projects found')
    else:
        print('Error: {}'.format(r.status_code))


@projects.command('init', help='Initialize project in current directory.')
@click.pass_context
@login_required
def projects_init(ctx):
    home = os.getcwd()
    if not Project.is_uid_valid(os.path.basename(home)):
        project_uid = click.prompt('Please enter a valid project name')
        home = os.path.join(home, project_uid)

    if create_project(ctx, None, home):
        click.echo('Project is initialized in current directory.')


@projects.command('create', help='Create project in new directory.')
@click.argument('name', type=str)
@click.pass_context
@login_required
def projects_create(ctx, name):
    home = os.path.join(os.getcwd(), name)
    if create_project(ctx, None, home):
        click.echo('Project is created in directory {}.'.format(home))


def projects_clone(ctx, path, directory, include, exclude):
    conn = ctx.obj['connection']

    values = path.split('/')
    account_uid = conn.account_uid

    if len(values) == 3:
        try:
            account_uid, projects_dir, project_uid = values
            assert (projects_dir == 'projects')
        except:
            click.echo('Invalid project path. Please use <account_uid>/projects/<uid>')
            return
    else:
        click.echo('Invalid project path. Please use <account_uid>/projects/<uid>')
        return

    # check project path, account_uid, project_uid
    if directory is None:
        home = os.path.join(os.getcwd(), project_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the project exisits
    r = conn.get('{}/accounts/{}/projects/{}'.format(conn.URL, account_uid, project_uid))
    if r.status_code == 200:
        remote_project = r.json()
    elif r.status_code == 401 or r.status_code == 404:
        print('Project does not exist.')
        return
    else:
        print('Error: {}'.format(r.status_code))
        return

    if not Project.exists_remote(project_uid, remote_project):
        click.echo('There is no project {}/projects/{} on the server'.format(account_uid, project_uid))
        return

    can_create = True
    if Project.exists_local(home):
        can_create = click.confirm('Project already exists, overwrite?')
    if not can_create:
        return

    # git clone
    git = GitWrapper()
    if not exclude and not include:
        exclude = '*'
    if git.lfs_clone(home, account_uid, project_uid, include=include, exclude=exclude) == 0:
        Project(account_uid, project_uid).save(home)
        git.exclude(home, Project.EXCLUSIONS)


