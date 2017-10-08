# -*- coding: utf-8 -*-
# Copyright © 2017 ACSONE SA/NV
# License GPLv3 (http://www.gnu.org/licenses/gpl-3.0-standalone.html)

import os
import subprocess

import pytest
import yaml


class Config:

    def __init__(self, tmpdir_factory):
        self.cache_dir = tmpdir_factory.mktemp('cache')
        self.config_dir = tmpdir_factory.mktemp('config')
        self.work_dir = tmpdir_factory.mktemp('work')
        os.environ['GIT_AUTOSHARE_CACHE_DIR'] = str(self.cache_dir)
        os.environ['GIT_AUTOSHARE_CONFIG_DIR'] = str(self.config_dir)

    def write_repos_yml(self, d):
        yaml.dump(d, self.config_dir.join('repos.yml').open('w'))


@pytest.fixture(scope='function')
def config(tmpdir_factory):
    return Config(tmpdir_factory)


def test_prefetch_all(config):
    config.write_repos_yml({
        'github.com': {
            'mis-builder': [
                'OCA',
                'acsone',
            ],
        },
    })
    host_dir = config.cache_dir.join('github.com')
    subprocess.check_call(['git', 'prefetch'])
    assert host_dir.check(dir=1)
    assert host_dir.join('mis-builder').join('objects').check(dir=1)
    subprocess.check_call(['git', 'prefetch'])


def test_prefetch_one(config):
    config.write_repos_yml({
        'github.com': {
            'mis-builder': [
                'OCA',
                'acsone',
            ],
            'git-aggregator': [
                'acsone',
            ],
        },
    })
    host_dir = config.cache_dir.join('github.com')
    subprocess.check_call([
        'git', 'prefetch', 'https://github.com/acsone/git-aggregator.git'])
    assert host_dir.check(dir=1)
    assert host_dir.join('git-aggregator').join('objects').check(dir=1)
    assert host_dir.join('mis-builder').check(exists=0)
    r = subprocess.call([
        'git', 'prefetch', 'https://github.com/acsone/notfound.git'])
    assert r != 0


def test_clone_no_repos_yml(config):
    clone_dir = config.work_dir.join('git-aggregator')
    subprocess.check_call([
        'git', 'clone', 'https://github.com/acsone/git-aggregator.git',
        str(clone_dir)])
    assert clone_dir.join('.git').check(dir=1)
    assert config.cache_dir.join('github.com').join('git-aggregator').\
        join('objects').check(exists=0)


def test_clone(config):
    config.write_repos_yml({
        'github.com': {
            'mis-builder': [
                'OCA',
                'acsone',
            ],
            'git-aggregator': [
                'acsone',
            ],
        },
    })
    clone_dir = config.work_dir.join('git-aggregator')
    subprocess.check_call([
        'git', 'clone', 'https://github.com/acsone/git-aggregator.git',
        str(clone_dir)])
    # check clone succeeded
    assert clone_dir.join('.git').check(dir=1)
    # check prefetch in cache succeeded
    assert config.cache_dir.join('github.com').join('git-aggregator').\
        join('objects').check(dir=1)