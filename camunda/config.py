#
# camunda rest config
#

import click
import configparser
import os

# configurable constants
MY_FILE = '~/.camunda-rest-engine.config'
MY_SECTION = 'camunda-rest-engine'
MY_KEY = 'url'
MY_USER = 'username'
MY_PASS = 'password'

my_config = configparser.ConfigParser()


def readConfig(filename):
    # expand '~/' to real pathnames
    pathname = os.path.expanduser(filename)
    my_config.read(pathname)

def writeConfig(filename):
    # expand '~/' to real pathnames
    pathname = os.path.expanduser(filename)
    with open(pathname, 'w') as configfile:
        my_config.write(configfile)

def getKey(keyName):
    return my_config[MY_SECTION][keyName]


@click.group()
def config():
    pass

#
# read api key from config file
#
@click.command()
@click.option('--config', '-c', default=MY_FILE)
def show(config):
    readConfig(config)
    if not my_config.has_section(MY_SECTION):
        click.echo('Config file not defined: ' + config)
        return
    my_section = my_config[MY_SECTION]
    if MY_KEY not in my_section:
        click.echo(MY_KEY + ' Key Not Defined.  Use SET command.')
        return
    my_key = my_section[MY_KEY]
    click.echo(MY_KEY + ' Key: ' + my_key)

#
# write my_key to config file
#
@click.command()
@click.argument(MY_KEY)
@click.argument(MY_USER)
@click.argument(MY_PASS)
@click.option('--config', '-c', default=MY_FILE)
def set(url, username, password, config):
    readConfig(config)
    if not my_config.has_section(MY_SECTION):
        my_config[MY_SECTION] = {}
    my_section = my_config[MY_SECTION]
    my_section[MY_KEY] = url
    my_section[MY_USER] = username
    my_section[MY_PASS] = password
    writeConfig(config)
    click.echo(MY_KEY + ' Key written to ' + config)


config.add_command(show)
config.add_command(set)

if __name__ == '__main__':
    config()
