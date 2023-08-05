"""
Job commands
"""
import os
import sys
import json
import subprocess
import threading
import base64

import click
import websocket

from onepanel.commands.base import APIViewController
from onepanel.commands.login import login_required


class JobViewController(APIViewController):

    def __init__(self, conn):

        super(JobViewController, self).__init__(conn)

        project = self.get_project()

        self.endpoint = '{root}/accounts/{account_uid}/projects/{project_uid}/jobs'.format(
            root=self.conn.URL,
            account_uid=project.account_uid,
            project_uid=project.project_uid
        )


@click.group(help='Job commands group')
@click.pass_context
def jobs(ctx):
    ctx.obj['vc'] = JobViewController(ctx.obj['connection'])
    ctx.obj['project'] = ctx.obj['vc'].get_project()

@jobs.command('create', help='Execute a command on a remote machine in the current project')
@click.argument(
    'command',
    type=str
)
@click.option(
    '-m', '--machine-type',
    type=str,
    required=True,
    help='Machine type ID'
)
@click.option(
    '-e', '--environment',
    type=str,
    required=True,
    help='Instance template ID'
)
@click.pass_context
@login_required
def create_job(ctx, command, machine_type, environment):
    new_job = {
        'command': command,
        'machineType': {
            'uid': machine_type
        },
        'instanceTemplate': {
            'uid': environment
        }
    }

    created_job = ctx.obj['vc'].post(post_object=new_job)

    if created_job:
        print('New job created: {}'.format(created_job['uid']))

    return


@jobs.command('list', help='Show commands executed on remote machines')
@click.option(
    '-a', '--all',
    type=bool,
    is_flag=True,
    default=False,
    help='Include finished commands'
)
@click.pass_context
@login_required
def list_jobs(ctx, all):
    vc = ctx.obj['vc']
    items = vc.list(params='?running=true' if not all else '')

    if items is None or len(items) == 0:
        print('No jobs found. Use "--all" flag to retrieve completed jobs.')
        return

    vc.print_items(items, fields=['uid', 'command'], field_names=['ID', 'COMMAND'])

@jobs.command('stop', help='Stop a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def kill_job(ctx, job_uid):
    ctx.obj['vc'].delete(job_uid, field_path='/active', message_on_success='Job stopped', message_on_failure='Job not found')

@jobs.command('logs', help='Show a log of the command')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def job_logs(ctx, job_uid):
    vc = ctx.obj['vc']
    project = ctx.obj['project']
    
    job = vc.get(job_uid)
    if job is None:
        print('Job not found.')
        return

    if job['active'] == 0:
        log = vc.get(job_uid, field_path='/logs')
        print(log)
    else:
        # Streaming via WebSocket
        # See https://pypi.python.org/pypi/websocket-client/

        def on_message(ws, message):
            if message[0] == '0':
                message = base64.b64decode(message[1:]).decode('utf-8','ignore')
                sys.stdout.write(message)
                sys.stdout.flush()

        def on_error(ws, error):
            if isinstance(error, websocket.WebSocketConnectionClosedException):
                return

            if isinstance(error, KeyboardInterrupt):
                return

            if error.status_code == 502 or error.status_code == 503:
                print('Job {} is preparing'.format(job_uid))
            else:
                print(error)

        def on_close(ws):
            print('connection closed')

        def on_open(ws):
            def send_auth_token(*args):
                ws.send(json.dumps({'Authtoken': ''}))
            threading.Thread(target=send_auth_token).start()
        
        ws_url = '{ws_root}/{account_uid}/projects/{project_uid}/jobs/{job_uid}/logs/ws?id_token={token}'.format(
            ws_root='wss://c.onepanel.io',
            account_uid=project.account_uid,
            project_uid=project.project_uid,
            job_uid=job_uid,
            token=ctx.obj['connection'].token
        )
        
        ws = websocket.WebSocketApp(
            url=ws_url,
            on_message=on_message,
            on_open=on_open,
            on_error=on_error
        )
        
        ws.run_forever()

    return False

def jobs_download_output(ctx, path, directory):
    #
    # Resource
    #
    dirs = path.split('/')

    # Job output: Method 2
    # <account_uid>/projects/<project_uid>/jobs/<job_uid>
    if len(dirs) == 5:
        try:
            account_uid, projects_dir, project_uid, jobs_dir, job_uid = dirs
            assert (projects_dir == 'projects') and (jobs_dir == 'jobs')
        except:
            print('Incorrect job path')
            return None
    else:
        print('Incorrect job uid')
        return None

    #
    # Directory
    #
    if directory is None or directory == '.':
        home = os.getcwd()
    else:
        home = os.path.join(os.getcwd(), directory)

    #
    # Clone
    #
    cmd = (
            'rm -rf .onepanel_download'   # Cleaning after previous errors to avoid "is not an empty directory" error
            ' && git lfs clone --quiet -b job-{job_uid} https://{host}/{account_uid}/{project_uid}-output.git .onepanel_download'
            ' && cp -r .onepanel_download/jobs/{job_uid}/output/ {dir}'
            ' && rm -rf .onepanel_download'
        ).format(
            host='git.onepanel.io',
            account_uid=account_uid,
            project_uid=project_uid,
            job_uid=job_uid,
            dir=home
        )
    p = subprocess.Popen(cmd, shell=True)
    p.wait()

    if p.returncode == 0:
        print('Job output downloaded to: {dir}'.format(dir=home))
        return True
    else:
        print('Unable to download')
        return False

@jobs.command('delete', help='Delete a job')
@click.argument(
    'job_uid',
    type=str
)
@click.pass_context
@login_required
def delete_job(ctx, job_uid):
    ctx.obj['vc'].delete(job_uid, message_on_success='Job deleted', message_on_failure='Job not found')