from setuptools import setup

setup(
    name="onepanel",
    version='1.0.1',
    packages = ['onepanel', 'onepanel.commands'],
    install_requires=[
        'requests',
        'click',
        'PTable',
        'configobj',
        'websocket-client',
        'humanize'
    ],
    entry_points='''
        [console_scripts]
        onepanel=onepanel.cli:cli
    ''',
)
