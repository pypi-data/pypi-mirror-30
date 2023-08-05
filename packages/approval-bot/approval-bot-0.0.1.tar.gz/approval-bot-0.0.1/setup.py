"""
Setup.py for approval-bot CLI
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='approval-bot',
    version='0.0.1',
    description='Deployment approvals via Slack',
    long_description='A CLI to request approvals via Slack approval bot',
    url='https://github.com/danielwhatmuff/approval-bot',
    author='Daniel Whatmuff',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='travis circle jenkins bitbucket gitlab deployment slack approval approvals',
    py_modules=["approval-bot"],
    install_requires=['slackclient', 'requests', 'boto3'],
    scripts=['bin/approval-bot'],
)
