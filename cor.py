import click
import fscontroller as fs
import gitcontroller as gc
import os
import shutil
import json

KNOWNLANGUAGES = {
	"Swift": "https://github.com/bahusvel/COR-Framework-Swift.git",
	"Python": "https://github.com/bahusvel/COR-Framework-Python.git",
	"GO": "https://github.com/bahusvel/COR-Framework-GO"
}

CORFRAMEWORK = "https://github.com/bahusvel/COR-Framework"
CORCLI = "https://github.com/bahusvel/COR-CLI.git"
CORINDEX = "https://github.com/bahusvel/COR-Index.git"
CORCLISTORAGE = click.get_app_dir("COR CLI")
STORAGEINDEX = CORCLISTORAGE+"/index"
STORAGE_LOCAL_INDEX = CORCLISTORAGE+"/localindex"
STORAGEMODULES = STORAGEINDEX+"/modules"


class TYPE:
	MODULE = "MODULE"
	RECIPE = "RECIPE"
	FRAMEWORK = "FRAMEWORK"
	UNKNOWN = "UNKNOWN"

@click.group()
def cor():
	click.echo("Welcome to COR-CLI!")

@click.group()
def module():
	pass

@click.group()
def framework():
	pass

@click.group()
def recipe():
	pass

@click.command()
@click.option('--name', prompt=True)
def new_module(name):
	new_cor_entity(name)
	language = click.prompt("Please enter the language ", type=click.Choice(list(KNOWNLANGUAGES.keys()) + ["OTHER"]))
	if language == "OTHER":
		language_url = click.prompt("Enter the url for language repo instead: ")
	else:
		language_url = KNOWNLANGUAGES[language]
	if not os.path.exists("cor"):
		gc.gitaddsubmodule(language_url, pathname="cor")
	# initialize .cor directory
	create_corfile(name, TYPE.MODULE, language_url)

@click.command()
@click.option('--language', prompt=True)
def new_framework(language):
	name = "COR-Framework-" + language
	new_cor_entity(name)
	gc.gitaddsubmodule(CORFRAMEWORK)
	# initialize .cor directory

@click.command()
@click.option('--name', prompt=True)
def new_recipe(name):
	new_cor_entity(name)
	# initialize .cor directory

@click.command()
@click.option("--name")
def remove(name):
	if name is None and check_for_cor():
		name = os.getcwd()
	elif name is None:
		name = click.prompt("Name")
	shutil.rmtree(name)


@click.command()
def sync():
	sync_backend()


def sync_backend():
	commited = False
	if check_for_cor():
		if gc.getremote() != "":
			if gc.isdiff():
				if click.confirm("You have modified the module do you want to commit?"):
					msg = click.prompt("Please enter a commit message")
					gc.gitupsync(msg)
					commited = True
			gc.gitpull()
			if commited:
				gc.gitpush()
		else:
			click.secho("You do not have git remote setup", err=True)
			if click.confirm("Do you want one setup automatically?"):
				gc.github_login()
				name = read_corfile(os.getcwd() + "/.cor/corfile.json")["name"]
				remote = gc.github_create_repo(name).clone_url  # breaks sometimes, maybe doesnt return repo properly
			else:
				click.secho("You will have to create a repository manually and provide the clone url")
				remote = click.prompt("Please enter the url")
			gc.addremote(remote)
			gc.gitadd(".")
			gc.gitcommit("Initlizaing repo")
			gc.gitpush(create_branch=True)
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)


@click.command()
@click.option("--searchmethod", type=click.Choice(["QUICK", "FULL"]))
@click.argument("search_term")
def module_search(search_term, searchmethod):
	if searchmethod is None:
		searchmethod = "QUICK"
	modules = search_backend(search_term, entity_type=TYPE.MODULE, searchtype=searchmethod)
	for module in modules:
		cordict = read_corfile(STORAGEMODULES+"/"+module)
		click.secho("{} @ {}".format(cordict["name"], cordict["repo"]))


@click.command()
@click.option("--new-index")
def update(new_index):
	if new_index is not None:
		shutil.rmtree(STORAGEINDEX)
	if not os.path.exists(CORCLISTORAGE):
		os.mkdir(CORCLISTORAGE)
	if not os.path.exists(STORAGEINDEX):
		os.chdir(CORCLISTORAGE)
		if new_index is not None:
			gc.gitclone(new_index, aspath="index")
		else:
			gc.gitclone(CORINDEX, aspath="index")
	else:
		os.chdir(STORAGEINDEX)
		gc.gitpull()


@click.command()
@click.option("--local/--remote", default=False)
def upgrade(local):
	if not os.path.exists(CORCLISTORAGE):
		os.mkdir(CORCLISTORAGE)
	if not local:
		if not os.path.exists(CORCLISTORAGE+"/cli"):
			os.chdir(CORCLISTORAGE)
			gc.gitclone(CORCLI, aspath="cli")
		os.chdir(CORCLISTORAGE+"/cli")
		gc.gitpull()
	if not local:
		os.system("pip install --upgrade .")
	else:
		os.system("pip install --upgrade --editable .")


@click.command()
def publish():
	entity_location = os.getcwd()
	if check_for_cor():
		username = gc.github_login().get_user().login
		sync_backend()
		remote = gc.getremote()
		localindex = gc.get_cor_index()
		if localindex is None:
			localindex = gc.fork_on_github("bahusvel/COR-Index")
		if not os.path.exists(STORAGE_LOCAL_INDEX):
			os.chdir(CORCLISTORAGE)
			gc.gitclone(localindex.clone_url, aspath="localindex")
		os.chdir(STORAGE_LOCAL_INDEX)
		gc.gitpull()
		# create corfile here
		local_cordict = read_corfile(entity_location + "/.cor/corfile.json")
		local_cordict["repo"] = remote
		if local_cordict["type"] == "MODULE":
			prefix = "modules"
		else:
			prefix = "modules"
		public_name = local_cordict["name"].lower()
		public_corfile_path = STORAGE_LOCAL_INDEX+"/" + prefix + "/" + public_name + ".json"
		write_corfile(local_cordict, public_corfile_path)
		gc.gitadd(public_corfile_path)
		gc.gitcommit("Added " + public_name)
		gc.gitpush()
		try:
			gc.github_pull_request(localindex.full_name, username, "COR-Index", "Add " + public_name)
		except Exception:
			click.secho("Pull request failed, please create one manualy", err=True)
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)


@click.command()
@click.option("--url", prompt=True)
def get_module(url):
	if get_type() == TYPE.RECIPE:
		# add module to recipe correctly
		pass
	gc.gitclone(url)


@click.command()
@click.argument("commands", nargs=-1)
def git(commands):
	os.system("git " + " ".join(commands))


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


def create_corfile(name, type, language):
	if check_for_cor():
		cordict = {"name": name, "type": type, "language": language}
		cdir = os.getcwd()
		write_corfile(cordict, cdir+"/.cor/corfile.json")


def read_corfile(path_to_corfile):
	with open(path_to_corfile, 'r') as local_corfile:
			local_cordict = json.loads(local_corfile.read())
	return local_cordict


def write_corfile(cordict, path_to_corfile):
	with open(path_to_corfile, 'w') as corfile:
			json.dump(cordict, corfile)


def search_backend(term, searchtype="QUICK", entity_type=TYPE.MODULE):
	searchpath = STORAGEMODULES
	if entity_type == TYPE.MODULE:
		searchpath = STORAGEMODULES
	if searchtype == "QUICK":
		items = os.listdir(searchpath)
		return list(filter(lambda x: term in x, items))
	elif searchtype == "FULL":
		pass
	else:
		raise Exception("Invalid search method " + searchtype)


def get_type():
	return None


def check_for_cor():
	return os.path.exists(".cor")

# module commands
module.add_command(new_module, name="new")
module.add_command(remove)
module.add_command(get_module, name="get")
module.add_command(sync)
module.add_command(publish)
module.add_command(module_search, name="search")
# framework commands
framework.add_command(new_framework, name="new")
framework.add_command(remove)
framework.add_command(sync)
framework.add_command(publish)
framework.add_command(remove)
# recipe commands
recipe.add_command(new_recipe, name="new")
recipe.add_command(remove)
recipe.add_command(get_module)
recipe.add_command(sync)
recipe.add_command(publish)
recipe.add_command(remove)
# main menu
cor.add_command(framework)
cor.add_command(module)
cor.add_command(recipe)
cor.add_command(sync)
cor.add_command(update)
cor.add_command(upgrade)
cor.add_command(publish)
cor.add_command(remove)
cor.add_command(git)

if __name__ == '__main__':
	cor()