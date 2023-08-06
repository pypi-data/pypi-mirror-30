#!/usr/bin/env python3
import sys
import os
import json
import argparse
import requests
import datetime
from datetime import datetime, timezone, date, timedelta

API_NAME = "analytics"
API_VERSION = "v3"

# Declare and use command-line flags.
cl_args_parser = argparse.ArgumentParser(add_help=False)

cl_args_parser.add_argument('--start_date', type=str, nargs='?', default=(datetime.today() - timedelta(
    days=90)).strftime('%Y-%m-%d'), help=('Start date for query. If not specified default is 90 days ago'))
cl_args_parser.add_argument('--end_date', type=str, nargs='?', default=datetime.today().strftime(
    '%Y-%m-%d'), help=('End date for query. If not specified default is 90 days ago'))
cl_args_parser.add_argument('--start_index', type=str, nargs='?', default='1', help=('Start Index for query'))
cl_args_parser.add_argument('--max_results', type=str, nargs='?', default='10000', help=('Max results per query'))
cl_args_parser.add_argument('--set_profile', type=str, nargs='?', default='available',
                            help=('Declare whether to use available Profile ids or custom ids'))
cl_args_parser.add_argument('--generate_profile', type=str, nargs='?', default='no',
                            help=('Auto generate available profile parameters'))

cli_args = cl_args_parser.parse_args()

from cifl_auth_wrapper import cifl_auth

home_dir = os.getcwd()


# try:
#     run_config = json.load(open(home_dir + '/config/run_config.json'))
# except Exception as e:
#     cifl_auth.exit_error(e)


def get_profile_details(service):
    # service = cifl_auth.get_service()
    # Use the Analytics service object to get the first profile id.

    # Get a list of all Google Analytics accounts for the authorized user.
    accounts = service.management().accounts().list().execute()
    account_ids = []
    profile_details = []
    if accounts.get('items'):
        # Get the first Google Analytics account.
        accounts = accounts.get('items')

        for account in accounts:
            account_ids.append(account.get('id'))

        for account_id in account_ids:
            # Get a list of all the properties for the first account.
            properties = service.management().webproperties().list(
                accountId=account_id).execute()

            if properties.get('items'):
                # Get the first property id.

                for prop in properties.get('items'):
                    # property = properties.get('items')[0].get('id')
                    property = prop.get('id')

                    # Get a list of all views (profiles) for the first property.
                    profiles = service.management().profiles().list(
                        accountId=account_id,
                        webPropertyId=property).execute()

                    if profiles.get('items'):
                        # return the first view (profile) id.
                        profile_details.append(
                            {'id': profiles.get('items')[0].get('id'), 'webPropertyId': profiles.get('items')[0].get(
                                'webPropertyId'), 'websiteUrl': profiles.get('items')[0].get('websiteUrl'),
                             'name': profiles.get('items')[0].get('name')})

        # write profile ids to file
        available_profiles = {'profile_details': profile_details}

        with open(os.getcwd() + '/config/params/available_profiles.json', 'w') as outfile:
            json.dump(available_profiles, outfile)
        # return profile_details

    return None


# def get_results(service, profile_id):
#     # Use the Analytics Service Object to query the Core Reporting API
#     # for the number of sessions in the past seven days.
#     return service.data().ga().get(
#         ids='ga:' + profile_id,
#         start_date='30daysAgo',
#         end_date='today',
#         metrics='ga:sessions').execute()


def get_mcf_data(profile_id, oauth2token):
    HEADERS = {'Authorization': 'Bearer {}'.format(oauth2token)}

    url = 'https://www.googleapis.com/analytics/v3/data/mcf?ids=ga%3A' + profile_id + \
          '&start-date=' + cli_args.start_date + '&end-date=' + cli_args.end_date + \
          '&metrics=mcf%3AtotalConversions%2Cmcf%3AassistedConversions' + \
          '&max-results=' + cli_args.max_results + \
          '&start-index=' + cli_args.start_index + \
          '&dimensions=mcf%3Asource%2Cmcf%3Amedium%2Cmcf%3AbasicChannelGroupingPath%2Cmcf%3AconversionDate%2Cmcf%3AconversionGoalNumber%2Cmcf%3AconversionDate%2Cmcf%3AcampaignName'

    try:
        with requests.Session() as sess:
            sess.headers.update(HEADERS)
            response = (sess.get(url)).json()
    except Exception as e:
        logger = cifl_auth.error_logger()
        logger.error(e)
        return None

    return response


def to_singer_format(response):
    import singer

    schema = cifl_auth.load_schema('ga_mcf_schema')

    singer.write_schema('ga_mcf', schema, [])

    logger = cifl_auth.error_logger()

    # Check for error in response
    if response is None:
        singer.write_records('ga_mcf', [
            {'Profile_ID': 'Null', 'Profile_Name': 'Null', 'Date': '', 'Channel_Group_Path': '', 'Source': '',
             'Medium': '', 'Conversion_Goal_Number': '', 'Assisted_Conversion': ''}])
        return

    if 'error' in response:
        logger.error('Error Code: %s Error Message: %s',
                     response['error']['code'], response['error']['message'])
        if (response['error']['code'] == 401):
            cifl_auth.get_auth()
            print("Re-authentication complete")
        sys.exit()

    # Check for empty results
    profileId = response['profileInfo']['profileId']
    profileName = response['profileInfo']['profileName']

    if 'rows' not in response:
        logger.error(
            '0 results returned for profile ID: %s Profile Name: %s:', profileId, profileName)
        singer.write_records('ga_mcf', [
            {'Profile_ID': profileId, 'Profile_Name': profileName, 'Date': '', 'Channel_Group_Path': '', 'Source': '',
             'Medium': '', 'Conversion_Goal_Number': '', 'Assisted_Conversion': ''}])
        return

    # Populate for all rows returned
    rows = response['rows']

    for row in rows:
        channel_group_path = ''
        assisted_conversions = row[8]['primitiveValue']
        conversion_goal_number = row[4]['primitiveValue']
        medium = row[1]['primitiveValue']
        source = row[0]['primitiveValue']

        raw_channel_group_paths = row[2]['conversionPathValue']
        count = len(raw_channel_group_paths)
        for raw_channel_group_path in raw_channel_group_paths:
            channel_group_path += raw_channel_group_path['nodeValue']
            if (count > 1):
                channel_group_path += '->'
                count = count - 1

        date = row[3]['primitiveValue']
        formatted_date = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
        singer.write_records('ga_mcf', [{'Profile_ID': profileId, 'Profile_Name': profileName, 'Date': formatted_date,
                                         'Channel_Group_Path': channel_group_path, 'Source': source,
                                         'Medium': medium, 'Conversion_Goal_Number': conversion_goal_number,
                                         'Assisted_Conversion': assisted_conversions}])


def main(argv):
    service = cifl_auth.get_service(API_NAME, API_VERSION)

    if service is None:
        print("Authentication just completed, please run the code again")
        sys.exit()

    if cli_args.generate_profile == 'yes':
        get_profile_details(service)
        print('available profiles successfully generated')
        sys.exit()

    oauth2token = cifl_auth.get_auth_access_token()

    if oauth2token is None:
        cifl_auth.get_auth()
        return

    try:
        profile_details = cifl_auth.load_params('available_profiles')
    except Exception as e:
        cifl_auth.exit_error(e)

    if ((cli_args.set_profile).lower() == "custom"):
        try:
            profile_details = cifl_auth.load_schema('custom_profiles')
        except Exception as e:
            cifl_auth.exit_error(e)

    for profile_detail in profile_details['profile_details']:
        to_singer_format(get_mcf_data(profile_detail['id'], oauth2token))
