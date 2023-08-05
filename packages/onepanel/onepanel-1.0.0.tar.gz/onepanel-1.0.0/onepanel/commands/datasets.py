""" Command line interface for the OnePanel Machine Learning platform

'Datasets' commands group.
"""

import os
import configobj
import json
import re
import click
import subprocess

import humanize
from prettytable import PrettyTable
from onepanel.commands.login import login_required
from onepanel.gitwrapper import GitWrapper


class Dataset:
    """ Datasets data model
    """

    DATASET_FILE = '.onepanel/dataset'
    EXCLUSIONS = ['.onepanel/dataset']

    def __init__(self, account_uid=None, dataset_uid=None):
        self.account_uid = account_uid
        self.dataset_uid = dataset_uid

    def save(self, home):
        if not os.path.exists(home):
            os.makedirs(home)
        onepanel_dir = os.path.join(home, '.onepanel')
        if not os.path.exists(onepanel_dir):
            os.makedirs(onepanel_dir)
        dataset_file = os.path.join(home, Dataset.DATASET_FILE)

        cfg = configobj.ConfigObj(dataset_file)
        cfg['uid'] = self.dataset_uid
        cfg['account_uid'] = self.account_uid
        cfg.write()

    @classmethod
    def from_json(cls, data):
        dataset = cls(data['account']['uid'], data['uid'])
        return dataset

    @classmethod
    def from_directory(cls, home):
        if not Dataset.exists_local(home):
            return None

        dataset_file = os.path.join(home, Dataset.DATASET_FILE)
        cfg = configobj.ConfigObj(dataset_file)
        dataset = cls(cfg['account_uid'], cfg['uid'])
        return dataset

    @staticmethod
    def is_uid_valid(uid):
        pattern = re.compile('^[a-z0-9][-a-z0-9]{1,23}[a-z0-9]$')
        if pattern.match(uid):
            return True
        else:
            return False

    @staticmethod
    def exists_local(home):
        dataset_file = os.path.join(home, Dataset.DATASET_FILE)
        if os.path.isfile(dataset_file):
            return True
        else:
            return False

    @staticmethod
    def exists_remote(dataset_uid, data):
        exists = False
        if data['uid'] == dataset_uid:
            exists = True
        return exists

    @staticmethod
    def print_list(data):
        if len(data) == 0:
            print('No datasets found')
            return

        tbl = PrettyTable(border=False)
        tbl.field_names = ['NAME', 'VERSIONS', 'SIZE']
        tbl.align = 'l'
        for row in data:
            tbl.add_row([row['uid'], row['statistics']['versionCount'], humanize.naturalsize(row['statistics']['size'], binary=True)])
        print(tbl)


def create_dataset(ctx, account_uid, home):
    """ Dataset creation method for 'datasets_init' and 'datasets_create'
    commands
    """

    conn = ctx.obj['connection']

    if not account_uid:
        account_uid = conn.account_uid

    dataset_uid = os.path.basename(home)
    if not Dataset.is_uid_valid(dataset_uid):
        click.echo('Dataset name {} is invalid.'.format(dataset_uid))
        click.echo('Name should be 3 to 25 characters long, lower case alphanumeric or \'-\' and must start and end with an alphanumeric character.')
        return None

    r = conn.get('{}/accounts/{}/datasets/{}'.format(conn.URL, account_uid, dataset_uid))
    if r.status_code == 200:
        remote_dataset = r.json()
    else:
        print('Error: {}'.format(r.status_code))
        return None

    dataset = None
    if Dataset.exists_remote(dataset_uid, remote_dataset):
        if Dataset.exists_local(home):
            click.echo('Dataset is already initialized')
        else:
            dataset = Dataset(account_uid, dataset_uid)
            dataset.save(home)
            git = GitWrapper()
            git.init(home, account_uid, dataset_uid + '_dataset')
            git.exclude(home, Dataset.EXCLUSIONS)

    else:
        can_create = True
        if Dataset.exists_local(home):
            can_create = click.confirm(
                'Dataset exists locally but does not exist in {}, create the dataset and remap local folder?'
                .format(account_uid))

        if can_create:
            url = '{}/accounts/{}/datasets'.format(conn.URL, account_uid)
            data = {
                'uid': dataset_uid
            }
            r = conn.post(url, data=json.dumps(data))

            if r.status_code == 200:
                dataset = Dataset.from_json(r.json())
                dataset.save(home)
                git = GitWrapper()
                git.init(home, account_uid, dataset_uid + '_dataset')
                git.exclude(home, Dataset.EXCLUSIONS)
            else:
                print('Error: {}'.format(r.status_code))

    return dataset

@click.group(help='Dataset commands group')
@click.pass_context
def datasets(ctx):
    pass


@datasets.command('list', help='Display a list of all datasets.')
@click.pass_context
@login_required
def datasets_list(ctx):
    conn = ctx.obj['connection']
    url = '{}/datasets'.format(conn.URL)

    r = conn.get(url)
    if r.status_code == 200:
        Dataset.print_list(r.json())
    elif r.status_code == 404:
        print('No datasets found')
    else:
        print('Error: {}'.format(r.status_code))


@datasets.command('init', help='Initialize dataset in current directory.')
@click.pass_context
@login_required
def datasets_init(ctx):
    home = os.getcwd()
    if not Dataset.is_uid_valid(os.path.basename(home)):
        dataset_uid = click.prompt('Please enter a valid dataset name')
        home = os.path.join(home, dataset_uid)

    if create_dataset(ctx, None, home):
        click.echo('Dataset is initialized in current directory.')


@datasets.command('create', help='Create dataset in new directory.')
@click.argument('name', type=str)
@click.pass_context
@login_required
def datasets_create(ctx, name):
    home = os.path.join(os.getcwd(), name)
    if create_dataset(ctx, None, home):
        click.echo('Dataset is created in directory {}.'.format(home))


def datasets_clone(ctx, path, directory, include, exclude):
    conn = ctx.obj['connection']

    values = path.split('/')
    account_uid = conn.account_uid

    if len(values) == 3:
        try:
            account_uid, datasets_dir, dataset_uid = values
            assert (datasets_dir == 'datasets')
        except:
            click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
            return
    else:
        click.echo('Invalid dataset path. Please use <account_uid>/datasets/<uid>')
        return

    # check dataset path, account_uid, dataset_uid
    if directory is None:
        home = os.path.join(os.getcwd(), dataset_uid)
    elif directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    # check if the dataset exisits
    r = conn.get('{}/accounts/{}/datasets/{}'.format(conn.URL, account_uid, dataset_uid))
    if r.status_code == 200:
        remote_dataset = r.json()
    elif r.status_code == 401 or r.status_code == 404:
        print('Project does not exist.')
        return
    else:
        print('Error: {}'.format(r.status_code))
        return None

    if not Dataset.exists_remote(dataset_uid, remote_dataset):
        click.echo('There is no dataset {}/datasets/{} on the server'.format(account_uid, dataset_uid))
        return

    can_create = True
    if Dataset.exists_local(home):
        can_create = click.confirm('Dataset already exists, overwrite?')
    if not can_create:
        return

    # git clone
    git = GitWrapper()
    code = git.lfs_clone(home, account_uid, dataset_uid, ext='_dataset', include=include, exclude=exclude)
    if code == 0:
        Dataset(account_uid, dataset_uid).save(home)
        git.exclude(home, Dataset.EXCLUSIONS)
    
    return code

def datasets_download(ctx, path, directory):
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    cmd = 'rm -rf .onepanel_download'
    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    code = datasets_clone(ctx, path, '.onepanel_download', include='*', exclude='')
    if code != 0:
        return False
    
    cmd = (
        'cp -r .onepanel_download/* {dir}'
        '&& rm -rf .onepanel_download'
    ).format(
        dir=home
    )
    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    if p.returncode == 0:
        print('The files downloaded to: {dir}'.format(dir=home))
        return True
    else:
        print('Unable to download')
        return False

