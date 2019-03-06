#
# Manage OpsGenie Alerts in Bulk
#
# Author: Chris Maeda (cmaeda@cmaeda.com)

#
# Example Usage
#
# 1. count open alerts in Dec 2018
# python3 alerts.py count -s open --since 2018-12-01 --before 2019-01-01
#
# 2. view open alerts in Dec 2018
# python3 alerts.py list -s open --since 2018-12-01 --before 2019-01-01
#
# 3. close open alerts in Dec 2018
# python3 alerts.py close --since 2018-12-01 --before 2019-01-01
#
# 4. delete closed alerts in Dec 2018
# python3 alerts.py delete -s closed --since 2018-12-01 --before 2019-01-01
#
# 5. prune alerts caused by API limits
#
# python3 alerts.py prune --since 2018-12-01 --before 2019-01-01
#
# Alerts caused by API limits have the string 'You are making too many requests!'
# in the alert description.
#
# Note that the close and delete commands first perform a list query,
# then they call close or delete on the alert records returned by the query.
#
# All commands, other than count, take offset and limit args
# which control paged access to the result set of the list query.
#

import click
import requests
import json
import datetime

# config module
from config import opsgenie_config, readConfig, getApiKey

#
# Implement Alerts Commands
#
# These are wrappers around the Alerts REST API
# See https://docs.opsgenie.com/docs/alert-api
#

#
# Makes an opsgenie alert search query.
# See https://docs.opsgenie.com/docs/alerts-search-query-help
#
# status should be 'open' / 'closed'
# before and since should be 'YYYY-mm-DD', e.g. '2018-12-01'
def alert_makequery(status, before, since):
    query = None
    if status != None:
        query = 'status:' + status
    if before != None:
        # parse to datetime then convert to unix timestamp
        datebefore = datetime.datetime.strptime(before, '%Y-%m-%d')
        datebeforets = int(datebefore.timestamp())
        beforeterm = 'lastOccurredAt < ' + str(datebeforets)
        if query != None:
            query = query + ' AND ' + beforeterm
        else:
            query = beforeterm
    if since != None:
        # parse to datetime then convert to unix timestamp
        datesince = datetime.datetime.strptime(since, '%Y-%m-%d')
        datesincets = int(datesince.timestamp())
        sinceterm = 'lastOccurredAt >= ' + str(datesincets)
        if query != None:
            query = query + ' AND ' + sinceterm
        else:
            query = sinceterm
    return query

# Count matching alert records
# See https://docs.opsgenie.com/docs/alert-api#section-count-alerts
def alerts_getcount(apiKey, query):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    if query != None:
        params = {'query': query}
    else:
        params = {}
    resp = requests.get('https://api.opsgenie.com/v2/alerts/count', headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    respjsondata = respjson['data']['count']
    return respjsondata

# List matching alert records
# See https://docs.opsgenie.com/docs/alert-api#section-list-alerts
# offset and limit control paging in the result set
def alerts_list(apiKey, query, offset, limit):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    if query != None:
        params = {'query': query}
    else:
        params = {}
    params['offset'] = offset
    params['limit'] = limit
    
    resp = requests.get('https://api.opsgenie.com/v2/alerts', headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    respjsondata = respjson['data']
    return respjsondata

# Get a single alert using its id
# See https://docs.opsgenie.com/docs/alert-api#section-get-alert
def alerts_get(apiKey, alertId):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    resp = requests.get('https://api.opsgenie.com/v2/alerts/' + alertId, headers=headers)
    if resp.status_code != 200:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    respjsondata = respjson['data']
    return respjsondata

# Close a single alert using its id
# The user, source, and note arguments are attached to the closure record
# See https://docs.opsgenie.com/docs/alert-api#section-close-alert
def alerts_close(apiKey, alertId, user, source, note):
    headers = {'Authorization': 'GenieKey ' + apiKey, 'Content-Type': 'application/json'}
    data = {}
    if user != None:
        data["user"] = user
    if source != None:
        data["source"] = source
    if note != None:
        data["note"] = note
    # must parse json to string so that requests package passes it through without modification
    postdata = json.dumps(data)
    resp = requests.post('https://api.opsgenie.com/v2/alerts/' + alertId + '/close', headers=headers, data=postdata)
    if resp.status_code != 202:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson

# Delete a single alert using its id
# See https://docs.opsgenie.com/docs/alert-api#section-delete-alert
def alerts_delete(apiKey, alertId):
    headers = {'Authorization': 'GenieKey ' + apiKey}
    resp = requests.delete('https://api.opsgenie.com/v2/alerts/' + alertId, headers=headers)
    if resp.status_code != 202:
        raise Exception(resp.status_code, resp.text)
    respjson = json.loads(resp.text)
    return respjson


#
# Code to implement the command line interface using the click package.
# See https://click.palletsprojects.com/en/7.x/
#

@click.group()
def alerts():
    pass

@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--status', '-s')
@click.option('--before')
@click.option('--since', '--after')
def count(config, status, before, since):
    readConfig(config)
    apiKey = getApiKey()
    query = alert_makequery(status, before, since)
    try:
        res = alerts_getcount(apiKey, query)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Alert Count ' + str(res))
    return res

@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--status', '-s')
@click.option('--before')
@click.option('--since', '--after')
@click.option('--offset', '-o', default=0)
@click.option('--limit', '-l', default=20)
def list(config, status, before, since, offset, limit):
    readConfig(config)
    apiKey = getApiKey()
    query = alert_makequery(status, before, since)
    try:
        res = alerts_list(apiKey, query, offset, limit)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Alert Count ' + str(len(res)))
    for adef in res:
        al_id = adef['id']
        adata = alerts_get(apiKey, al_id)
        al_alias = adata['alias']
        al_status = adata['status']
        al_desc = adata['description']
        al_createdAt = adata['createdAt']
        
        click.echo('Alert ' + al_alias + ' createdAt:' + al_createdAt + ' status:' + al_status + ' desc:' + al_desc)
        click.echo()
    return res

#
# delete alerts matching criteria
#
@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--status', '-s')
@click.option('--before')
@click.option('--since', '--after')
@click.option('--offset', '-o', default=0)
@click.option('--limit', '-l', default=20)
def delete(config, status, before, since, offset, limit):
    readConfig(config)
    apiKey = getApiKey()
    query = alert_makequery(status, before, since)
    try:
        res = alerts_list(apiKey, query, offset, limit)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Alert Count ' + str(len(res)))
    for adef in res:
        al_id = adef['id']
        try:
            delres = alerts_delete(apiKey, al_id)
            click.echo('Deleted Alert ' + al_id)
        except Exception as exc:
            click.echo('Error: opsgenie api returned error ' + str(exc.args))
            return None
    return res

#
# close alerts matching criteria
#
@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--before')
@click.option('--since', '--after')
@click.option('--offset', '-o', default=0)
@click.option('--limit', '-l', default=20)
def close(config, before, since, offset, limit):
    readConfig(config)
    apiKey = getApiKey()
    query = alert_makequery('open', before, since)
    try:
        res = alerts_list(apiKey, query, offset, limit)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Alert Count ' + str(len(res)))
    for adef in res:
        al_id = adef['id']
        try:
            delres = alerts_close(apiKey, al_id, None, None, None)
            click.echo('Closed Alert ' + al_id)
        except Exception as exc:
            click.echo('Error: opsgenie api returned error ' + str(exc.args))
            return None
    return res

#
# close false-positive alerts caused by API limits
#
@click.command()
@click.option('--config', '-c', default='~/.opsgenie.config')
@click.option('--before')
@click.option('--since', '--after')
@click.option('--offset', '-o', default=0)
@click.option('--limit', '-l', default=20)
def prune(config, before, since, offset, limit):
    readConfig(config)
    apiKey = getApiKey()
    query = alert_makequery('open', before, since)
    try:
        res = alerts_list(apiKey, query, offset, limit)
    except Exception as exc:
        click.echo('Error: opsgenie api returned error ' + str(exc.args))
        return None
    click.echo('Alert Count ' + str(len(res)))
    for adef in res:
        al_id = adef['id']
        adata = alerts_get(apiKey, al_id)
        al_alias = adata['alias']
        al_status = adata['status']
        al_desc = adata['description']
        al_createdAt = adata['createdAt']
        
        if 'You are making too many requests!' in al_desc:
            click.echo('Alert ' + al_alias + ' caused by OpsGenie API limits (id:' + al_id + ')')
            try:
                res = alerts_close(apiKey, al_id, 'devops', None, 'Close Api Limit Alert')
            except Exception as exc:
                click.echo('Error: opsgenie api returned error ' + str(exc.args))
                return None
            click.echo('Closed Alert ' + al_id)
        else:
            click.echo('Alert ' + al_createdAt + ' alias:' + al_alias + 'status:' + al_status + ' Ignored')
    return res


alerts.add_command(count)
alerts.add_command(list)
alerts.add_command(delete)
alerts.add_command(close)
alerts.add_command(prune)

if __name__ == '__main__':
    alerts()

    

