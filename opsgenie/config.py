#
# opsgenie config
#

import click
import configparser
import os

opsgenie_config = configparser.ConfigParser()

def readConfig(filename):
    # expand '~/' to real pathnames
    pathname = os.path.expanduser(filename)
    opsgenie_config.read(pathname)

def writeConfig(filename):
    # expand '~/' to real pathnames
    pathname = os.path.expanduser(filename)
    with open(pathname, 'w') as configfile:
        opsgenie_config.write(configfile)

def getApiKey():
    return opsgenie_config['opsgenie.com']['GenieKey']

@click.group()
def config():
    pass

#
# read api key from config file
#
@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
def show(config):
    readConfig(config)
    if not opsgenie_config.has_section('opsgenie.com'):
        click.echo('Config file not defined: ' + config)
        return
    opsgenie = opsgenie_config['opsgenie.com']
    if 'GenieKey' not in opsgenie:
        click.echo('OpsGenie API Key Not Defined.  Use SET command.')
        return
    genieKey = opsgenie['GenieKey']
    click.echo('OpsGenie API Key: ' + genieKey)

#
# write api key to config file
#
@click.command()
@click.argument('apikey')
@click.option('--config', '-c', default='~/.opsgenie.config')
def set(apikey, config):
    readConfig(config)
    if not opsgenie_config.has_section('opsgenie.com'):
        opsgenie_config['opsgenie.com'] = {}
    opsgenie = opsgenie_config['opsgenie.com']
    opsgenie['GenieKey'] = apikey
    writeConfig(config)
    click.echo('OpsGenie API Key written to ' + config)


config.add_command(show)
config.add_command(set)

if __name__ == '__main__':
    config()
