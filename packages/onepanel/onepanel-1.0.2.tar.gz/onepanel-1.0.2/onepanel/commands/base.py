"""
View-Controller class for OnePanel API
"""
import os
import sys
import json
from prettytable import PrettyTable

from onepanel.commands.projects import Project


class APIViewController:

    conn = None     # Connection from onepanel.cli
    endpoint = str

    def __init__(self, conn):

        self.conn = conn

    # Wrappers for HTTP requests
    def get(self, uid, field_path='', params=None):
        """Get a JSON object from the endpoint"""
        
        r = self.conn.get('{endpoint}/{uid}{field_path}{params}'.format(endpoint=self.endpoint, uid=uid, field_path=field_path, params=params or ''))

        c = r.status_code
        if c == 200:
            if r.headers['Content-Type'] == 'text/plain':
                item = r.text
            else:
                item = r.json()
        else:
            return None

        return item

    def list(self, params=None):
        """Get a JSON list from the endpoint"""
        
        r = self.conn.get('{endpoint}{params}'.format(endpoint=self.endpoint, params=params or ''))

        c = r.status_code
        if c == 200:
            items = r.json()
        else:
            return None

        return items

    def post(self, post_object):
        """POST an object and return the newly created resource"""

        r = self.conn.post(self.endpoint, data=json.dumps(post_object))

        c = r.status_code
        if c == 200:
            created_object = r.json()
        else:
            print('Error: {}'.format(c))
            return None

        return created_object

    def delete(self, uid, field_path='', message_on_success='Resource deleted', message_on_failure='Resource not found'):
        r = self.conn.delete('{}/{}{}'.format(self.endpoint, uid, field_path))

        c = r.status_code
        if c == 200:
            print('{message}: {id}'.format(message=message_on_success, id=uid))
            return True
        elif c == 404:
            print('{message}: {id}'.format(message=message_on_failure, id=uid))
        else:
            print('Error: {}'.format(c))

        return False

    # Support functions

    @staticmethod
    def get_project():
        """Retrieve the project from the local storage and return it"""

        local_project = Project.from_directory(os.getcwd())

        if local_project is None:
            # Return error before reaching other CLI commands:
            print('This project is not initialized, type "onepanel init" to initialize this project')
            sys.exit(1)
        else:
            return local_project

    @staticmethod
    def print_items(
            items,
            fields=None,
            field_names=None,
            empty_message='No items found'
    ):
        """A standard table for showing response to GET requests"""

        if fields is None:
            fields = ['uid', 'name']
        if field_names is None:
            field_names=['ID', 'NAME']

        if len(items) == 0:
            print(empty_message)
            return items

        summary = PrettyTable(border=False)
        summary.field_names = field_names
        summary.align = 'l'
        for item in items:
            summary.add_row([item[field] for field in fields])
        print(summary)

