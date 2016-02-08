import json
import os

import gitcontroller as gc


def read_corfile(path_to_corfile):
	with open(path_to_corfile, 'r') as local_corfile:
			local_cordict = json.loads(local_corfile.read())
	return local_cordict


def write_corfile(cordict, path_to_corfile):
	with open(path_to_corfile, 'w') as corfile:
			json.dump(cordict, corfile)


def new_cor_entity(name):
	if not os.path.exists(name):
		os.mkdir(name)
	os.chdir(name)
	if not check_for_cor():
		os.mkdir(".cor")
	if not git_exists():
		gc.gitinit()


def git_exists():
	return os.path.exists(".git")


def check_for_cor():
	return os.path.exists(".cor")