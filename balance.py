#!/usr/bin/python

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
import re
import datetime as dt
import dateutil.parser
from dateutil import tz

balance = 0

def days_remaining():
    hoje = dt.date.today()
    if dt.date.today().day < 5:
        dia_pagamento = hoje.replace(day=5)
        return (dia_pagamento - hoje).days
    else:
        dia_pagamento = dt.date.today().replace(day=5, month=hoje.month+1)
        return (dia_pagamento - hoje).days

def find_last_update(file_metadata):
    return file_metadata.get('modifiedDate')

def humanize_date(uct_date_string):
    # receives a date string and converts it to a brt localized date string
    local_tz = tz.gettz('BRT')
    date = dateutil.parser.parse(uct_date_string)
    local_date = date.astimezone(local_tz)
    return local_date.strftime("%d-%m-%y %H:%M %Z")

def fetch():
    global balance
    # Creating an oauth state machine
    gauth = GoogleAuth()

    if not gauth.LoadCredentialsFile('credentials.json'):
        # credentials.json' not found. Initiating a full complete auth flow
        gauth.CommandLineAuth()
        gauth.SaveCredentialsFile('credentials.json')

    # Credentials loaded!

    MATEHACKERS_FINANCES_DOCUMENT_ID = "0Ar6ELBV64QUxdHQza0M1bHdOcEJNcUNGelJmRThMcVE"

    FINANCE_SHEET_METADATA = {
        u'exportLinks': {
            u'text/csv': u'https://docs.google.com/feeds/download/spreadsheets/Export?key='+ MATEHACKERS_FINANCES_DOCUMENT_ID+ '&exportFormat=csv'
        }
    }

    # Metadata given by FetchMetadata() is incomplete, it doesn't have the
    # exportLink key for csv format so I have to inject it manually
    file = GoogleDriveFile(gauth, metadata={ "id": MATEHACKERS_FINANCES_DOCUMENT_ID }, uploaded=True)
    file.FetchMetadata()
    metadata_copy = file.metadata.copy()
    metadata_copy.update(FINANCE_SHEET_METADATA)
    file.metadata = metadata_copy

    # I couldn't make GetConstentString() that was supposed to bring the text
    # only instead of saving a file to work, that's why I am saving a file here
    file.GetContentFile('result.csv', mimetype='text/csv')

    regex = re.compile("Em caixa:,\"(-?\d+,?\d*)\"")

    # Since we were 'forced' to get a file now we have to read it.
    with open('result.csv','r') as f:
        for line in f:
            m = regex.search(line)
            if m:
                balance = m.groups(0)[0]

    last_update = find_last_update(file)

    return {
        'balance': balance,
        'lastUpdate': last_update,
        'daysRemaining': days_remaining(),
        'lastUpdateHuman': humanize_date(last_update)
    }

