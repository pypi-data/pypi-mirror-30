# System imports
import os
from os.path import join

from git import *
from nose.tools import *

from PyGitUp.tests import basepath, init_master, update_file

test_name = 'diverged-rebase'
repo_path = join(basepath, test_name + os.sep)


def setup():
    master_path, master = init_master(test_name)

    # Prepare master repo
    master.git.checkout(b=test_name)

    # Modify file in master
    update_file(master, '1', filename='a.txt')
    update_file(master, '2', filename='b.txt')

    # Clone to test repo
    path = join(basepath, test_name)

    master.clone(path, b=test_name)
    repo = Repo(path, odbt=GitCmdObjectDB)

    assert repo.working_dir == path

    # Modify file in our repo (feature branch)
    repo.git.checkout(b='feature_' + test_name)
    update_file(repo, 'feature', filename='a.txt')
    repo.git.push('--set-upstream', 'origin', 'feature_' + test_name)

    # Modify file in origin repo
    update_file(master, '3', filename='b.txt')

    # Rebase onto master
    repo.git.pull(rebase=True)
    repo.git.rebase(test_name)


def test_diverged_rebase():
    """ Run 'git up' with result: diverged """
    os.chdir(repo_path)

    from PyGitUp.gitup import GitUp
    gitup = GitUp(testing=True)
    gitup.run()

    print(basepath)

    # assert_equal(len(gitup.states), 2)
    # assert_equal(gitup.states[0], 'diverged')
    assert_equal(True, False)
