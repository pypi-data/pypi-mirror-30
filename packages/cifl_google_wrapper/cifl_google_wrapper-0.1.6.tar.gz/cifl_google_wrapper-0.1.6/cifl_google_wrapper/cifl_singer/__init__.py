def to_singer_format(response):

    import singer

    schema = load_schema('ga_mcf_schema')

    singer.write_schema('ga_mcf', schema, [])

    logger = error_logger()

    # Check for error in response
    if response is None:
        singer.write_records('ga_mcf', [{'Profile ID': 'Null', 'Profile Name': 'Null', 'Date': '', 'Channel Group Path': '', 'Source': '',
                                         'Medium': '', 'Conversion Goal Number': '', 'Assisted Conversion': ''}])
        return

    if 'error' in response:
        logger.error('Error Code: %s Error Message: %s',
                     response['error']['code'], response['error']['message'])
        if(response['error']['code'] == 401):
            print(
                "To authenticate run:  python ga-mcf.py 'client_secrets.json' --run_auth=yes")
        sys.exit()

    # Check for empty results
    profileId = response['profileInfo']['profileId']
    profileName = response['profileInfo']['profileName']
    
    if 'rows' not in response:
        logger.error(
            '0 results returned for profile ID: %s Profile Name: %s:', profileId, profileName)
        singer.write_records('ga_mcf', [{'Profile ID': profileId, 'Profile Name': profileName, 'Date': '', 'Channel Group Path': '', 'Source': '',
                                         'Medium': '', 'Conversion Goal Number': '', 'Assisted Conversion': ''}])
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
            if(count > 1):
                channel_group_path += '->'
                count = count - 1

        date = row[3]['primitiveValue']
        formatted_date = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
        singer.write_records('ga_mcf', [{'Profile ID': profileId, 'Profile Name': profileName, 'Date': formatted_date, 'Channel Group Path': channel_group_path, 'Source': source,
                                         'Medium': medium, 'Conversion Goal Number': conversion_goal_number, 'Assisted Conversion': assisted_conversions}])

