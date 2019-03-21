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

def procdef_get(procDefId):
    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-definition/' + procDefId

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson


# set history_time_to_live
def procdef_set_hittl(procDefId, hittl):
    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-definition/' + procDefId + '/history-time-to-live'

    my_user = getKey('username')
    my_pass = getKey('password')

    my_data = '{"historyTimeToLive":' + str(hittl) + '}'
    
    headers = {'Content-Type': 'application/json'}
    resp = requests.put(my_url, auth=HTTPBasicAuth(my_user, my_pass), data=my_data, headers=headers)
    if resp.status_code != 204:
        raise Exception(resp.status_code, resp.text)

#
# list process defs for tenantid and/or deploymentid
#
def procdef_list(tenantId, deploymentid):
    params = {}
    if tenantId != None:
        params['tenantIdIn'] = tenantId
    if deploymentid != None:
        params['deploymentId'] = deploymentid
        
    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-definition'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, params=params, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

def procdef_count(tenantId):
    if tenantId != None:
        params = {'tenantIdIn': tenantId}
    else:
        params = {}

    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-definition/count'
    
    my_user = getKey('username')
    my_pass = getKey('password')

    resp = requests.get(my_url, params=params, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

#
# get process instances for process definition, filtered by deployment
#
def procinst_for_procdefid(procDefId, deploymentid):
    params = {}
    if procDefId != None:
        params['processDefinitionId'] = procDefId
    if deploymentid != None:
        params['deploymentId'] = deploymentid

    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-instance'

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.get(my_url, auth=HTTPBasicAuth(my_user, my_pass), params=params)
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

#
# delete a process instance
#
def procinst_delete(procInstId):
    my_url = getKey('url')
    my_url = my_url + '/engine/default/process-instance/' + procInstId

    my_user = getKey('username')
    my_pass = getKey('password')
    
    resp = requests.delete(my_url, auth=HTTPBasicAuth(my_user, my_pass))
    if resp.status_code != 204:
        raise Exception(resp.status_code, resp.text)

#
# Code to implement the command line interface using the click package.
# See https://click.palletsprojects.com/en/7.x/
#

@click.group()
def procdef():
    pass

@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
def count(config, tenantid):
    readConfig(config)
    try:
        res = procdef_count(tenantid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(res))
    return res

@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
@click.option('--deploymentid', '-d')
@click.option('--showttl')
def list(config, tenantid, deploymentid, showttl):
    readConfig(config)
    try:
        res = procdef_list(tenantid, deploymentid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(len(res)))
    for adef in res:
        def_id = adef['id']
        def_key = adef['key']
        def_vers = adef['version']

        if showttl != None:
            my_procdef = procdef_get(def_id)
            def_hittl = my_procdef['historyTimeToLive']
            click.echo(def_key + ':' + str(def_vers) + ' id:' + def_id + ' ttl:' + str(def_hittl))
        else:
            click.echo(def_key + ':' + str(def_vers) + ' id:' + def_id)
    return res


@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
@click.option('--deploymentid', '-d')
def listinstances(config, tenantid, deploymentid):
    readConfig(config)
    try:
        res = procdef_list(tenantid, deploymentid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(len(res)))
    for adef in res:
        def_id = adef['id']
        def_key = adef['key']
        def_vers = adef['version']

        my_history = procinst_for_procdefid(def_id, deploymentid)
        
        click.echo(def_key + ':' + str(def_vers) + ' id:' + def_id + ' instances:' + str(len(my_history)))

        for phist in my_history:
            click.echo(json.dumps(phist))
            
    return res


#
# delete process instances
#
@click.command()
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
@click.option('--deploymentid', '-d')
def deleteinstances(config, tenantid, deploymentid):
    readConfig(config)
    try:
        res = procdef_list(tenantid, deploymentid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(len(res)))
    for adef in res:
        def_id = adef['id']
        def_key = adef['key']
        def_vers = adef['version']

        my_history = procinst_for_procdefid(def_id, deploymentid)
        
        click.echo(def_key + ':' + str(def_vers) + ' id:' + def_id + ' history:' + str(len(my_history)))

        for phist in my_history:
            procinst_id = phist['id']
            procinst_delete(procinst_id)
            click.echo('Deleted ' + procinst_id)
            
    return res


@click.command()
@click.argument('ttl')
@click.option('--config', '-c', default=MY_FILE)
@click.option('--tenantid', '-t')
@click.option('--deploymentid', '-d')
def sethistoryttl(ttl, config, tenantid, deploymentid):
    readConfig(config)
    try:
        res = procdef_list(tenantid, deploymentid)
    except Exception as exc:
        click.echo('Error: rest api returned error ' + str(exc.args))
        return None
    click.echo('Count ' + str(len(res)))
    for adef in res:
        def_id = adef['id']
        def_key = adef['key']
        def_vers = adef['version']
        procdef_set_hittl(def_id, ttl)
        click.echo('Updated:' + def_key + ':' + str(def_vers) + ' ttl:' + str(ttl) + ' id:' + def_id)
    return res


procdef.add_command(count)
procdef.add_command(list)
procdef.add_command(sethistoryttl)
procdef.add_command(listinstances)
procdef.add_command(deleteinstances)

if __name__ == '__main__':
    procdef()

    

