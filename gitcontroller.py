import os
import subprocess
import github

GITHUB = None

def gitclone(url, aspath=None):
	if aspath is None:
		os.system("git clone --recursive " + url)
	else:
		os.system("git clone --recursive " + url + " " + aspath)


def gitaddsubmodule(url, pathname=None):
	if pathname is not None:
		os.system("git submodule add " + url + " " + pathname)
	else:
		os.system("git submodule add " + url)
	cwd = os.getcwd()
	os.chdir(pathname)
	os.system("git submodule update --init --recursive")
	os.chdir(cwd)


def gitinit():
	os.system("git init")


def gitpull():
	os.system("git pull")


def gitadd(file):
	os.system("git add " + file)


def gitcommit(message):
	os.system("git commit -a -m " + "\"" + message + "\"")


def isdiff():
	diff = subprocess.check_output(["git", "diff", "--shortstat"], universal_newlines=True)
	return diff != ""


def gitpush():
	os.system("git push")


def getremote():
	out = subprocess.check_output(["git", "remote", "-v"], universal_newlines=True)
	if out == "":
		return out
	splits = out.split(" ")
	print(splits)
	return splits[1]


def addremote(url):
	os.system("git remote add origin " + url)


def github_login(username, password):
	global GITHUB
	GITHUB = github.Github(username, password)


def get_cor_index():
	if GITHUB is not None:
		for repo in GITHUB.get_user().get_repos():
			if repo.name == "COR-Index":
				return repo
		return None


def fork_on_github(repo="bahusvel/COR-Index"):
	if GITHUB is not None:
		reporepr = GITHUB.get_repo(repo)
		return GITHUB.get_user().create_fork(reporepr)


def gitupsync(message):
	os.system("git add .")
	os.system("git commit -a -m \"" + message + "\"")

