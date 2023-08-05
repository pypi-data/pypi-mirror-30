# encoding UTF-8

import pytest

import logging
LOG = logging.getLogger()


def pytest_addoption(parser):
    group = parser.getgroup('Redmine Integration')

    group.addoption('--redmine', action='store_true', 
        dest='redmine', default=False,
        help='Enable Redmine plugin')

    group.addoption('--redmine-username', action='store', 
        dest='redmine-username', default=False,
        help='Redmine username')

    group.addoption('--redmine-password', action='store', 
        dest='redmine-password', default=False,
        help='Redmine password')

    group.addoption('--redmine-url', action='store', 
        dest='redmine', default=False,
        help='Redmine URL')

