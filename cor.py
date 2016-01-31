import click
import fscontroller as fsc
import gitcontroller as gc
import os
import shutil

KNOWNLANGUAGES = {
	"Swift": "https://github.com/bahusvel/COR-Framework-Swift.git",
	"Python": "https://github.com/bahusvel/COR-Framework-Python.git",
	"GO": "https://github.com/bahusvel/COR-Framework-GO"
}

CORFRAMEWORK = "https://github.com/bahusvel/COR-Framework"
CORCLI = "https://github.com/bahusvel/COR-CLI.git"


class TYPE:
	MODULE = 1
	RECIPE = 2
	FRAMEWORK = 3
	UNKNOWN = 4

@click.group()
def cor():
	click.echo("Welcome to COR-CLI")

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
@click.option('--language')
@click.option('--language-url')
def newModule(name, language, language_url):
	new_cor_entity(name)
	lurl = language_url
	while lurl is None:
		if language in KNOWNLANGUAGES:
			lurl = KNOWNLANGUAGES[language]
			break
		lurl = click.prompt("Please enter language-url: ")
	gc.gitaddsubmodule(lurl, pathname="cor")
	# initialize .cor directory


@click.command()
@click.option('--language', prompt=True)
def newFramework(language):
	name = "COR-Framework-" + language
	new_cor_entity(name)
	gc.gitaddsubmodule(CORFRAMEWORK)
	# initialize .cor directory

@click.command()
@click.option('--name', prompt=True)
def newRecipe(name):
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
	if check_for_cor():
		pass
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)


@click.command()
def upgrade():
	pass

@click.command()
def publish():
	if check_for_cor():
		pass
	else:
		click.secho("Not a COR-Entity (Framework, Module, Recipe)", err=True)

@click.command()
@click.option("--url", prompt=True)
def get_module(url):
	if get_type() == TYPE.RECIPE:
		# add module to recipe correctly
		pass
	gc.gitclone(url)


def new_cor_entity(name):
	os.mkdir(name)
	os.chdir(name)
	os.mkdir(".cor")
	gc.gitinit()


def get_type():
	return None


def check_for_cor():
	return os.path.exists(".cor")

# module commands
module.add_command(newModule, name="new")
module.add_command(remove)
module.add_command(get_module, name="get")
module.add_command(sync)
module.add_command(publish)
# framework commands
framework.add_command(newFramework, name="new")
framework.add_command(remove)
framework.add_command(sync)
framework.add_command(publish)
framework.add_command(remove)
# recipe commands
recipe.add_command(newRecipe, name="new")
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
cor.add_command(upgrade)
cor.add_command(publish)
cor.add_command(remove)

if __name__ == '__main__':
	cor()