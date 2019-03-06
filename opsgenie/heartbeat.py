#
# Manage OpsGenie Heartbeats in Bulk
#
# Author: Chris Maeda (cmaeda@cmaeda.com)

import click
import requests
import json
import time

# config module
from config import opsgenie_config, readConfig, getApiKey

# implement heartbeat subcommands

def hb_getlist(apiKey):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    hblist = requests.get('https://api.opsgenie.com/v2/heartbeats', headers=headers)
    if hblist.status_code != 200:
        raise Exception(hblist.status_code, hblist.text)
    hbjson = json.loads(hblist.text)
    hbjsondata = hbjson['data']['heartbeats']
    return hbjsondata

# Get a heartbeat record
# See https://docs.opsgenie.com/docs/heartbeat-api#section-get-heartbeat-request
def hb_get(apiKey, name):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    hblist = requests.get('https://api.opsgenie.com/v2/heartbeats/' + name , headers=headers)
    if hblist.status_code != 200:
        raise Exception(hblist.status_code, hblist.text)
    hbjson = json.loads(hblist.text)
    hbjsondata = hbjson['data']
    return hbjsondata
    
def hb_patch(apiKey, name, timeout):
    patch = { 'interval': str(timeout) }
    patchjson = json.dumps(patch)
    headers = {'Authorization': 'GenieKey ' + apiKey, 'Content-Type': 'application/json'}
    hbresult = requests.patch('https://api.opsgenie.com/v2/heartbeats/' + name, headers=headers, data=patchjson)
    if hbresult.status_code != 200:
        raise Exception(hbresult.status_code, hbresult.text)
    hbjson = json.loads(hbresult.text)
    hbjsondata = hbjson['data']
    return hbjsondata


@click.group()
def heartbeat():
    pass

@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
def list(config):
    readConfig(config)
    apiKey = getApiKey()
    try:
        hbjson = hb_getlist(apiKey)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Heartbeat Count ' + str(len(hbjson)))
    for hbdef in hbjson:
        click.echo('Name: ' + hbdef['name'] + ' interval:' + str(hbdef['interval']))
    return hbjson

@click.command()
@click.argument('prefix')
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--showall', '-a')
def status(prefix, config, showall):
    readConfig(config)
    apiKey = getApiKey()
    try:
        hbjson = hb_getlist(apiKey)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    for hbdef in hbjson:
        hbname = hbdef['name']
        if not hbname.startswith(prefix):
            continue
        while True:
            try:
                hbdata = hb_get(apiKey, hbname)
                hbexpired = hbdata['expired']
                if hbexpired:
                    click.echo('Expired: ' + hbdef['name'] + ' interval:' + str(hbdef['interval']))
                elif showall == 'true':
                    click.echo('Healthy: ' + hbdef['name'] + ' interval:' + str(hbdef['interval']))
                break
            except Exception as exc:
                if exc.args[0] == 429:
                    # hit api limit, pause and try again
                    time.sleep(2)
                    continue
                else:
                    click.echo('Error: opsgenie api returned error ' + str(exc.args))
                    return None
    return hbjson

#
# bulk update on heartbeats matching prefix
#
@click.command()
@click.argument('prefix')
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--timeout', '-t')
def bulkset(prefix, config, timeout):
    if timeout == None:
        click.echo('Must specify --timeout option in minutes')
        return None
    timeout = int(timeout)
    readConfig(config)
    apiKey = getApiKey()
    click.echo('[ bulkset prefix=' + prefix + ' timeout=' + str(timeout) + ' ]')
    try:
        hbjson = hb_getlist(apiKey)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Heartbeat Count ' + str(len(hbjson)))
    for hbdef in hbjson:
        hbname = hbdef['name']
        if not hbname.startswith(prefix):
            # skip non-matching heartbeat record
            continue
        hbtimeout = hbdef['interval']
        if hbtimeout != timeout:
            # retry loop to patch heartbeat record
            while True:
                try:
                    hbres = hb_patch(apiKey, hbname, timeout)
                    click.echo('HB ' + hbname + ' timeout old:' + str(hbtimeout) + ' new:' + str(timeout))
                    break
                except Exception as exc:
                    if exc.args[0] == 429:
                        # hit api limit, pause and try again
                        time.sleep(2)
                        continue
                    else:
                        click.echo('Error: opsgenie api returned error ' + str(exc.args))
                        return None
    return hbjson


heartbeat.add_command(list)
heartbeat.add_command(bulkset)
heartbeat.add_command(status)

if __name__ == '__main__':
    heartbeat()
