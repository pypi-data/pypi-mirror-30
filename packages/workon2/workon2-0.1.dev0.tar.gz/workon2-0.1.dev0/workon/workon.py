#!/usr/bin/env python

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
activate_this_file = os.path.join(dir_path, "..", "env/bin/activate_this.py")
execfile(activate_this_file, dict(__file__=activate_this_file))

import sys
from shutil import copyfile
import yaml
import click

workon_home = os.path.join(os.path.expanduser("~"), ".workon")

# make sure we have ~/.workon dir
if not os.path.exists(workon_home):
    os.mkdir(workon_home)

local_file = os.path.join(".workon.yaml")

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

def get_config(project_name):
    config_file = os.path.join(workon_home, "{}.yaml".format(project_name))
    with open(config_file, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            raise(exc)
    # print("config = {}".format(config))
    include = os.path.join(config['path'], config['include']);
    with open(include, 'r') as stream:
        try:
            include_config = yaml.load(stream)
        except yaml.YAMLError as exc:
            raise(exc)
    del config['include']
    return merge_two_dicts(config, include_config)

@click.group()
def cli():
    pass

@cli.command()
def list():
    """List ects."""
    for project in os.listdir(workon_home):
        print project.replace(".yaml", "")

@cli.command()
def init():
    """Create .workon.yaml tempalte in CWD."""
    local_file = ".workon.yaml"
    if os.path.exists(local_file):
        return sys.stderr.write("{} already exists.\n".format(local_file))
    else:
        print("Write local project yaml to '{}'".format(local_file))
        template = os.path.join(dir_path, "templates", "project.yaml")
        copyfile(template, local_file)
    print("Done")

@cli.command()
@click.option('--name', type=str,
              help='Name of the project, defaults to directory-name.')
def add(name):
    """Add a project to workon."""
    if not name:
        name = os.path.basename(os.getcwd())

    config_file = os.path.join(workon_home, "{}.yaml".format(name))
    local_file = ".workon.yaml"

    if os.path.exists(config_file):
        return sys.stderr.write("Project already exists\n")

    if os.path.exists(local_file):
        print("Found .workon.yaml file in project, linking it")
        with open(config_file, 'w') as stream:
            stream.write('path: {}\n'.format(os.getcwd()))
            stream.write('include: ./.workon.yaml\n')
    else:
        print("Write project config file")
        template = os.path.join(dir_path, "templates", "project.yaml")
        with open(config_file, 'w') as config:
            config.write('path: {}\n'.format(os.getcwd()))
            with open(template, 'r') as template:
                config.write(template.read())

    print("Done")

@cli.command()
@click.argument('project_name')
@click.option('--silent', type=bool, default=False,
              help='Do not prompt.')
def delete(project_name, silent):
    """Delete a project from workon"""
    config_file = os.path.join(workon_home, "{}.yaml".format(project_name))

    if not os.path.exists(config_file):
        return sys.stderr.write("Project '{}' does not exist.\n".format(project_name))

    if input("Are you sure? (y/N) ") == "y":
        print("Delete {}".format(config_file))
        os.remove(config_file)
        print("Done")
    else:
        print("Cancelled")


@cli.command()
def install():
    """Install a project"""
    project_name = os.path.basename(os.getcwd())
    config = get_config(project_name)
    for script in config['install']:
        print("EXEC:{}".format(script))

@cli.command()
@click.option('--commands', type=str, multiple=True, default=['activate'],
              help='The project to work on.')
@click.argument('project_name')
def on(project_name, commands):
    """Start working on a project"""
    config = get_config(project_name)

    print("EXEC:cd {}".format(config['path']))

    for command in commands:
        scripts = config['commands'][command]
        for script in scripts:
            print("EXEC:{}".format(script))

if __name__ == '__main__':
    cli()
