#
# Camunda REST API
#
# Author: Chris Maeda (cmaeda@cmaeda.com)

import click
import requests
from requests.auth import HTTPBasicAuth
import json

# config module
from config import my_config, readConfig, getKey, MY_FILE

#
# REST API Calls
#

# Get history cleanup jobs
# See https://docs.camunda.org/manual/7.8/reference/rest/history/history-cleanup/get-history-cleanup-jobs/
def hcleanup_getjobs():
    my_url = getKey('url')
    my_url = my_url + '/engine/default/job'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

# Get history cleanup batch window config
# See https://docs.camunda.org/manual/7.8/reference/rest/history/history-cleanup/get-cleanup-configuration/
def hcleanup_getconfig():
    my_url = getKey('url')
    my_url = my_url + '/engine/default/history/cleanup/configuration'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

# Schedule a history cleanup
# See https://docs.camunda.org/manual/7.8/reference/rest/history/history-cleanup/post-history-cleanup/
# Note: docs say that result is not reliable but we return it anyway
def hcleanup_schedulejob(now):
    params = {}
    if now == False:
        params['executeAtOnce'] = 'false'

    my_url = getKey('url')
    my_url = my_url + '/engine/default/history/cleanup'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.post(my_url, auth=HTTPBasicAuth(my_user, my_pass), params=params)
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson


#
# Code to implement the command line interface using the click package.
# See https://click.palletsprojects.com/en/7.x/
#

@click.group()
def historycleanup():
    pass

@click.command()
@click.option('--config', '-c', default=MY_FILE)
def getjobs(config):
    readConfig(config)
    try:
        res = hcleanup_getjobs()
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None

    click.echo('Found ' + str(res) + ' jobs')
    for cjob in res:
        click.echo(json.dumps(cjob))
    return res


@click.command()
@click.option('--config', '-c', default=MY_FILE)
def getconfig(config):
    readConfig(config)
    try:
        res = hcleanup_getconfig()
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None

    click.echo('Got Config: ' + json.dumps(res))
    return res


@click.command()
@click.option('--config', '-c', default=MY_FILE)
def cleanup(config):
    readConfig(config)
    try:
        # True == run job now
        res = hcleanup_schedulejob(True)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None

    click.echo('Got Result: ' + json.dumps(res))
    return res



historycleanup.add_command(getjobs)
historycleanup.add_command(getconfig)
historycleanup.add_command(cleanup)

if __name__ == '__main__':
    historycleanup()

