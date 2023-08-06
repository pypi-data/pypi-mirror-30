#!/usr/bin/env python3

import argparse
import functools
import io
import os
import sys
import json
import logging
import collections
import threading
import http.client
import urllib
import pkg_resources

from jsonschema import validate
import singer

from cifl_auth_wrapper import cifl_auth

# home_dir = os.getcwd()

API_NAME = "sheets"
API_VERSION = "v4"

# try:
#     run_config = json.load(open(home_dir + '/config/run_config.json'))
# except Exception as e:
#     cifl_auth.exit_error(e)

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = singer.get_logger()


def emit_state(state):
    if state is not None:
        line = json.dumps(state)
        logger.debug('Emitting state {}'.format(line))
        sys.stdout.write("{}\n".format(line))
        sys.stdout.flush()

def create_sheet(service, spreadsheet_body):
    return service.spreadsheets().create(body=spreadsheet_body).execute()


def get_spreadsheet(service, spreadsheet_id):
    return service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

def get_spreadsheet_id(service):
    spreadsheet_id_path = os.path.join(os.getcwd(), 'config', 'targets', 'spreadsheet_id.json')
    spreadsheet_id = json.load(open(spreadsheet_id_path))

    if spreadsheet_id['id'] == "None":
        with open(spreadsheet_id_path, 'w') as f:
            new_empty_spreadsheet = create_sheet(service, {"properties": {"title": "CIFL Google Analytics"}})
            spreadsheet_id['id'] = new_empty_spreadsheet['spreadsheetId']
            json.dump(spreadsheet_id, f, ensure_ascii=False)

    return spreadsheet_id['id']

def get_values(service, spreadsheet_id, range):
    return service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range).execute()


def add_sheet(service, spreadsheet_id, title):
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 26
                            }
                        }
                    }
                }
            ]
        }).execute()


def append_to_sheet(service, spreadsheet_id, range, values):
    return service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range,
        valueInputOption='USER_ENTERED',
        body={'values': [values]}).execute()


def flatten(d, parent_key='', sep='__'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v) if type(v) is list else v))
    return dict(items)


def persist_lines(service, spreadsheet, lines):
    state = None
    schemas = {}
    key_properties = {}

    headers_by_stream = {}

    for line in lines:
        try:
            msg = singer.parse_message(line)
        except json.decoder.JSONDecodeError:
            logger.error("Unable to parse:\n{}".format(line))
            raise

        if isinstance(msg, singer.RecordMessage):
            if msg.stream not in schemas:
                raise Exception(
                    "A record for stream {} was encountered before a corresponding schema".format(msg.stream))

            schema = schemas[msg.stream]
            validate(msg.record, schema)
            flattened_record = flatten(msg.record)

            matching_sheet = [s for s in spreadsheet['sheets']
                              if s['properties']['title'] == msg.stream]
            new_sheet_needed = len(matching_sheet) == 0
            range_name = "{}!A1:ZZZ".format(msg.stream)
            append = functools.partial(
                append_to_sheet, service, spreadsheet['spreadsheetId'], range_name)

            if new_sheet_needed:
                add_sheet(service, spreadsheet['spreadsheetId'], msg.stream)
                # refresh this for future iterations
                spreadsheet = get_spreadsheet(
                    service, spreadsheet['spreadsheetId'])
                headers_by_stream[msg.stream] = list(flattened_record.keys())
                append(headers_by_stream[msg.stream])

            elif msg.stream not in headers_by_stream:
                first_row = get_values(
                    service, spreadsheet['spreadsheetId'], range_name + '1')
                if 'values' in first_row:
                    headers_by_stream[msg.stream] = first_row.get('values', None)[
                        0]
                else:
                    headers_by_stream[msg.stream] = list(
                        flattened_record.keys())
                    append(headers_by_stream[msg.stream])

            # order by actual headers found in sheet
            result = append([flattened_record.get(x, None)
                             for x in headers_by_stream[msg.stream]])

            state = None
        elif isinstance(msg, singer.StateMessage):
            logger.debug('Setting state to {}'.format(msg.value))
            state = msg.value
        elif isinstance(msg, singer.SchemaMessage):
            schemas[msg.stream] = msg.schema
            key_properties[msg.stream] = msg.key_properties
        else:
            raise Exception("Unrecognized message {}".format(msg))

    return state


def collect():
    try:
        version = pkg_resources.get_distribution('target-gsheet').version
        conn = http.client.HTTPSConnection(
            'collector.stitchdata.com', timeout=10)
        conn.connect()
        params = {
            'e': 'se',
            'aid': 'singer',
            'se_ca': 'target-gsheet',
            'se_ac': 'open',
            'se_la': version,
        }
        conn.request('GET', '/i?' + urllib.parse.urlencode(params))
        response = conn.getresponse()
        conn.close()
    except:
        logger.debug('Collection request failed')


def main():

    logger.info('Sending version information to Googlesheets. ')
                    # 'To disable sending anonymous usage data, set ' +
                    # 'the config parameter "disable_collection" to true')
    threading.Thread(target=collect).start()

    service = cifl_auth.get_service(API_NAME, API_VERSION)

    spreadsheet_id = get_spreadsheet_id(service)

    spreadsheet = get_spreadsheet(service, spreadsheet_id)

    input = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

    state = persist_lines(service, spreadsheet, input)

    emit_state(state)

    logger.debug("Exiting normally")