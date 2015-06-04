#!/usr/bin/python

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
from dateutil import tz
import re
import locale as l
import datetime as dt
import dateutil.parser
import requests

balance = 0
l.setlocale(l.LC_ALL, 'pt_BR.UTF8')

def fetch_unlock_balance():
    unlock_text = requests.get('https://unlock.fund/pt-BR/matehackers').text
    match = re.search(r'number\"\>(\d+)\</span.+arrecadados', unlock_text)
    return match.groups(0)[0]

def calculate_due_days():
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
    unlock_balance = fetch_unlock_balance()

    return {
        'unlockBalance': l.atof(unlock_balance),
        'totalBalance': l.atof(balance) + l.atof(unlock_balance),
        'balance': l.atof(balance),
        'lastUpdate': last_update,
        'daysRemaining': calculate_due_days(),
        'lastUpdateHuman': humanize_date(last_update)
    }

