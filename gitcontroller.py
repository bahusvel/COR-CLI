import os
import subprocess

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


def isdiff():
	diff = subprocess.check_output(["git", "diff", "--shortstat"], universal_newlines=True)
	return diff != ""


def gitpush():
	os.system("git push")


def gitupsync(message):
	os.system("git add .")
	os.system("git commit -a -m \"" + message + "\"")