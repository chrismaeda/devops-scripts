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

#
# list deployments for tenantid 
#
def deployment_list(tenantId):
    params = {}
    if tenantId != None:
        params['tenantIdIn'] = tenantId
        
    my_url = getKey('url')
    my_url = my_url + '/engine/default/deployment'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, params=params, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

# See https://docs.camunda.org/manual/7.8/reference/rest/deployment/get-query-count/
def deployment_count(tenantId):
    if tenantId != None:
        params = {'tenantIdIn': tenantId}
    else:
        params = {}

    my_url = getKey('url')
    my_url = my_url + '/engine/default/deployment/count'
    
    my_user = getKey('username')
    my_pass = getKey('password')

    resp = requests.get(my_url, params=params, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

#
# delete a process instance
#
def deployment_delete(deploymentId, doCascade, skipListeners, skipIoMappings):
    params = {}
    if doCascade == True:
        params['cascade'] = 'true'
    if skipListeners == True:
        params['skipCustomListeners'] = 'true'
    if skipIoMappings == True:
        params['skipIoMappings'] = 'true'
        
    my_url = getKey('url')
    my_url = my_url + '/engine/default/deployment/' + deploymentId

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.delete(my_url, auth=HTTPBasicAuth(my_user, my_pass), params=params)
    if resp.status_code != 204:
        raise Exception(resp.status_code, resp.text)

#
# Code to implement the command line interface using the click package.
# See https://click.palletsprojects.com/en/7.x/
#

@click.group()
def deployment():
    pass

@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
def count(config, tenantid):
    readConfig(config)
    try:
        res = deployment_count(tenantid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(res))
    return res

@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
def list(config, tenantid):
    readConfig(config)
    try:
        res = deployment_list(tenantid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(len(res)))
    for adef in res:
        def_id = adef['id']
        def_name = adef['name']
        def_tid = adef['tenantId']
        def_date = adef['deploymentTime']

        click.echo(def_name + ':' + def_tid + ' date:' + def_date + ' id:' + def_id)
    return res


@click.command()
@click.argument('deploymentid')
@click.option('--config', '-c', default=MY_FILE)
@click.option('--cascade', default=False)
@click.option('--skiplisteners', default=True)
@click.option('--skipio', default=True)
def delete(deploymentid, config, cascade, skiplisteners, skipio):
    readConfig(config)
    try:
        res = deployment_delete(deploymentid, cascade, skiplisteners, skipio)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Deleted ' + deploymentid)
    return res


deployment.add_command(count)
deployment.add_command(list)
deployment.add_command(delete)

if __name__ == '__main__':
    deployment()

    

