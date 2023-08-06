# WIP

def get_all_accounts(service):
    try:
        # Retrieve account list in pages and display data as we receive it.
        request = service.accounts().list(maxResults=MAX_PAGE_SIZE)

        while request is not None:
            result = request.execute()
            accounts = result['items']
            for account in accounts:
                print('Account with ID "%s" and name "%s" was found. '
                      % (account['id'], account['name']))

            request = service.accounts().list_next(request, result)

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


def fetch_adsense_reports(service, metrics, dimensions, sort_by):
    last_executed = get_timestamps()
    end_date = last_executed["end_date"]
    start_date = last_executed["start_date"]
    results = []

    try:
          # Let the user pick account if more than one.
        accounts = service.accounts().list().execute()

        for account in accounts['items']:
            account_id = account['id']
            result = service.accounts().reports().generate(
                accountId=account_id, startDate=start_date, endDate=end_date,
                metric=metrics,
                dimension=dimensions,
                sort=sort_by).execute()

            results.append(DataCollator([result]).collate_data())

        return results

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run the '
               'application to re-authorize')
        sys.exit()


def get_website_simple_revenue(adsense_service, google_sheets_service):
    metrics = ['PAGE_VIEWS', 'INDIVIDUAL_AD_IMPRESSIONS', 'CLICKS', 'EARNINGS']
    dimensions = ['DATE', 'AD_CLIENT_ID', 'DOMAIN_NAME']
    sort_by = ['+DOMAIN_NAME']

    results = fetch_adsense_reports(
        adsense_service, metrics, dimensions, sort_by)

    r1_data = []

    for result in results:
        if 'rows' in result:
            for row in result['rows']:
                website = row[2]
                date = row[0]
                page_views = row[3]
                impressions = row[4]
                clicks = row[5]
                estimated_earnings = row[6]
                r1_data.append([website, date, page_views,
                                impressions, clicks, estimated_earnings])
    r1_wsp_spreadsheet_id = get_spreadsheet_id(
        table_key='R1–WebsiteSimpleRevenue', service=google_sheets_service, sheet_title="R1 – Website Simple Revenue")
    range_name = "Sheet1!A1:F5"
    headers = [
        # Cell values ...
        ["Website", "Date", "Page Views", "Impressions",
            "Clicks", "Estimated Earnings (AUD)"],
        # Additional rows ...
    ]
    
    try:
        update_google_spreadsheet_headers(google_sheets_service, r1_wsp_spreadsheet_id, range_name, headers)
        append_google_spreadsheet_rows(google_sheets_service, r1_wsp_spreadsheet_id, range_name, values=r1_data)
        return None
    except Exception as e:
        exit_error(e)

def get_revenue_by_platform(adsense_service, google_sheets_service):
    metrics = ['PAGE_VIEWS', 'INDIVIDUAL_AD_IMPRESSIONS', 'CLICKS', 'EARNINGS']
    dimensions = ['DATE', 'AD_CLIENT_ID', 'DOMAIN_NAME', 'PLATFORM_TYPE_NAME']
    sort_by = ['+DOMAIN_NAME']

    results = fetch_adsense_reports(
        adsense_service, metrics, dimensions, sort_by)

    r1_data = []

    for result in results:
        if 'rows' in result:
            for row in result['rows']:
                website = row[2]
                date = row[0]
                platform = row[3]
                page_views = row[4]
                impressions = row[5]
                clicks = row[6]
                estimated_earnings = row[7]
                r1_data.append([website, date, platform, page_views,
                                impressions, clicks, estimated_earnings])

    r2_rbp_spreadsheet_id = get_spreadsheet_id(
        table_key='R2–RevenuebyPlatform', service=google_sheets_service, sheet_title="R2 – Revenue by Platform")
    range_name = "Sheet1!A1:G1"
    headers = [
        # Cell values ...
        ["Website", "Date", "Platform", "Page Views", "Impressions",
            "Clicks", "Estimated Earnings (AUD)"],
        # Additional rows ...
    ]
    
    try:
        update_google_spreadsheet_headers(google_sheets_service, r2_rbp_spreadsheet_id, range_name, headers)
        append_google_spreadsheet_rows(google_sheets_service, r2_rbp_spreadsheet_id, range_name, values=r1_data)
        return None
    except Exception as e:
       exit_error(e)

def get_revenue_by_AdUnit(adsense_service, google_sheets_service):
    metrics = ['PAGE_VIEWS', 'INDIVIDUAL_AD_IMPRESSIONS', 'CLICKS', 'EARNINGS']
    dimensions = ['DATE', 'AD_UNIT_NAME']
    sort_by = ['+AD_UNIT_NAME']

    results = fetch_adsense_reports(
        adsense_service, metrics, dimensions, sort_by)

    r1_data = []

    for result in results:
        if 'rows' in result:
            for row in result['rows']:
                ad_unit = row[1]
                date = row[0]
                page_views = row[2]
                impressions = row[3]
                clicks = row[4]
                estimated_earnings = row[5]
                r1_data.append([ad_unit, date, page_views,impressions, clicks, estimated_earnings])

    r3_rbau_spreadsheet_id = get_spreadsheet_id(
        table_key='R3–RevenuebyAdUnit', service=google_sheets_service, sheet_title="R3 – Revenue by Ad Unit")
    range_name = "Sheet1!A1:F1"
    headers = [
        # Cell values ...
        ["Ad Unit", "Date", "Page Views", "Impressions",
            "Clicks", "Estimated Earnings (AUD)"],
        # Additional rows ...
    ]
    
    try:
        update_google_spreadsheet_headers(google_sheets_service, r3_rbau_spreadsheet_id, range_name, headers)
        append_google_spreadsheet_rows(google_sheets_service, r3_rbau_spreadsheet_id, range_name, values=r1_data)
        return None
    except Exception as e:
        exit_error(e)

def get_revenue_by_AdUnit_by_platform(adsense_service, google_sheets_service):
    metrics = ['PAGE_VIEWS', 'INDIVIDUAL_AD_IMPRESSIONS', 'CLICKS', 'EARNINGS']
    dimensions = ['DATE', 'AD_UNIT_NAME', 'PLATFORM_TYPE_NAME']
    sort_by = ['+AD_UNIT_NAME']

    results = fetch_adsense_reports(
        adsense_service, metrics, dimensions, sort_by)

    r1_data = []

    for result in results:
        if 'rows' in result:
            for row in result['rows']:
                ad_unit = row[1]
                date = row[0]
                platform = row[2]
                page_views = row[3]
                impressions = row[4]
                clicks = row[5]
                estimated_earnings = row[6]
                r1_data.append([ad_unit, date, platform, page_views,impressions, clicks, estimated_earnings])

    r4_rbaubp_spreadsheet_id = get_spreadsheet_id(
        table_key='R4–RevenuebyAdUnitbyPlatform', service=google_sheets_service, sheet_title="R4 – Revenue by Ad Unit by Platform")
    range_name = "Sheet1!A1:G1"
    headers = [
        # Cell values ...
        ["Ad Unit", "Date", "Platform", "Page Views", "Impressions",
            "Clicks", "Estimated Earnings (AUD)"],
        # Additional rows ...
    ]
    
    try:
        update_google_spreadsheet_headers(google_sheets_service, r4_rbaubp_spreadsheet_id, range_name, headers)
        append_google_spreadsheet_rows(google_sheets_service, r4_rbaubp_spreadsheet_id, range_name, values=r1_data)
        return None
    except Exception as e:
        exit_error(e)