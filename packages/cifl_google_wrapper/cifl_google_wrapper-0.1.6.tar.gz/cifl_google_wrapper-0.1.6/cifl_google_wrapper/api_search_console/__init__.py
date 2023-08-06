#!/usr/bin/env python3
import sys
import os
import json
import argparse
from datetime import datetime, timezone, date, timedelta

from cifl_auth_wrapper import cifl_auth

API_NAME = "webmasters"
API_VERSION = "v3"

# Declare and use command-line flags.
cl_args_parser = argparse.ArgumentParser(add_help=False)

cl_args_parser.add_argument('--start_date', type=str, nargs='?', default=(datetime.today() - timedelta(
    days=90)).strftime('%Y-%m-%d'), help=('Start date for query. If not specified default is 90 days ago'))
cl_args_parser.add_argument('--end_date', type=str, nargs='?', default=datetime.today().strftime(
    '%Y-%m-%d'), help=('End date for query. If not specified default is 90 days ago'))
cl_args_parser.add_argument('--start_index', type=str,
                            nargs='?', default='1', help=('Start Index for query'))
cl_args_parser.add_argument('--max_results', type=str,
                            nargs='?', default='10000', help=('Max results per query'))
cl_args_parser.add_argument('--set_profile', type=str, nargs='?', default='available',
                            help=('Declare whether to use available Profile ids or custom ids'))
cl_args_parser.add_argument('--generate_profile', type=str, nargs='?', default='no',
                            help=('Auto generate available urls parameters'))

cli_args = cl_args_parser.parse_args()


def list_available_sites(service):
    site_entries = service.sites().list().execute()
    available_sites = {'urls': []}

    for site_entry in site_entries['siteEntry']:
        available_sites['urls'].append(site_entry['siteUrl'])

    with open(os.getcwd() + '/config/params/available_urls.json', 'w') as outfile:
        json.dump(available_sites, outfile)
    return None


def get_search_analytics_data(service, property_uri, request):
    """Executes a searchAnalytics.query request.

    Args:
      service: The webmasters service to use when executing the query.
      property_uri: The site or app URI to request data for.
      request: The request to be executed.

    Returns:
      An array of response rows.
    """

    try:
        response = service.searchanalytics().query(
            siteUrl=property_uri, body=request).execute()
    except Exception as e:
        logger = cifl_auth.error_logger()
        logger.error(e)
        return None

    return response


def to_singer_format(response, url):
    import singer

    schema = cifl_auth.load_schema('search_analytics_schema')

    singer.write_schema('my_search_analytics', schema, [])

    logger = cifl_auth.error_logger()

    # Check for error in response
    if response is None:
        singer.write_records('my_search_analytics', [
                             {'Requested_Object': url, 'Landing_Page': '', 'Date': '', 'Clicks': '', 'Impressions': '', 'CTR': '', 'Position': ''}])
        return

    if 'error' in response:
        logger.error('Error Code: %s Error Message: %s',
                     response['error']['code'], response['error']['message'])
        if(response['error']['code'] == 401):
            print(
                "To authenticate run:  search_analytics.py 'client_secrets.json' --run_auth=yes")
        sys.exit()

    if 'rows' not in response:
        logger.error('Warning: 0 results returned for site url: %s', url)
        singer.write_records('my_search_analytics', [
                             {'Requested_Object': url, 'Landing_Page': '', 'Date': '', 'Clicks': '', 'Impressions': '', 'CTR': '', 'Position': ''}])
        return

    # rows = response['rows']
    rows = sorted(response['rows'],
                  key=lambda row: row['impressions'], reverse=True)
    for row in rows:
        keys = ''
        # Keys are returned only if one or more dimensions are requested.
        if 'keys' in row:
            date = str(row['keys'][0])
            landing_page = str(row['keys'][1])
        # print(row)
        clicks = str(row['clicks'])
        impressions = str(row['impressions'])
        ctr = str(row['ctr'])
        position = str(row['position'])
        singer.write_records('my_search_analytics', [{'Requested_Object': url, 'Landing_Page': landing_page,
                                                      'Date': date, 'Clicks': clicks, 'Impressions': impressions, 'CTR': ctr, 'Position': position}])


def main(argv):

    service = cifl_auth.get_service(API_NAME, API_VERSION)

    if service is None:
        print("Authentication just completed, please run the code again")
        sys.exit()

    if cli_args.generate_profile == 'yes':
        list_available_sites(service)
        print('available profiles successfully generated')
        sys.exit()

    request = {
        'startDate': cli_args.start_date,
        'endDate': cli_args.end_date,
        'dimensions': ['date', 'page'],
        'rowLimit': 5000
    }

    urls = cifl_auth.load_params('available_urls')

    if cli_args.set_profile.lower() == "custom":
        urls = cifl_auth.load_params('custom_urls')

    # Loop through multiple  urls
    for url in urls['urls']:
        response = get_search_analytics_data(service, url, request)
        to_singer_format(response, url)
