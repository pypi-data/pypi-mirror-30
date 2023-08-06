import click
import json

from mccloud.tools import *
from mccloud.version import VERSION
import mccloud.constants

@click.group()
@click.option('--verbose', is_flag=True)
def main(verbose):
    if verbose:
        click.echo('We are in verbose mode')
    

@main.command()
@click.option('--env',
              help='This is the Terraform environment to grab the inventory from.')
@click.option('--playbook',
              help='This is the playbook you want to use.')
@click.option('--host',
              help='The host you want to run a command on.')
@click.option('--cmd',
              help='The command you want to run.')
def ansible(env, playbook, host, cmd):
    """Use Ansible to deploy to or run a command on a server"""
    if env is None:
        print("Environment is required")
        exit()

    if playbook:
      print('Deploying to Ansible')
      ansible_deploy(env, playbook)
    else:
      ansible_command(env, host, cmd)


@main.command()
@click.option('--env', default='scaffold',
              help='This is the Terraform environment to grab the inventory from.')
def terraform(env):
    """This option provisions resources using Terraform"""
    print('Deploying to Terraform')
    terraform_deploy(env)

@main.command()
def setup():
    """This option grabs all of the required tools that aren't on Pip"""
    install_tools(BINPATH)

@main.command()
@click.option('--dir',
              help='This is the name of the project directory')
def scaffold(dir):
    """This option builds the scaffolding for a new project"""
    build_scaffold(dir)

@main.command()
def version():
    print(VERSION)