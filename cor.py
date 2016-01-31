import click

@click.group()
def cor():
	click.echo("Welcome to COR-CLI")

@cor.command()
def module():
	pass

@cor.command()
def framework():
	pass

@cor.command()
def application():
	pass

if __name__ == '__main__':
	cor()