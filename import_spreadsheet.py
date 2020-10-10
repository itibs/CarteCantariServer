# Requirements:
# credentials.json
# token.pickle
# temp/<BOOK_ID> folder structure

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from normalizator import normalize
from cartecantari import BOOKS, get_book_json, get_song_json, save_song_json
from os import listdir
from os.path import isfile, join

MAX_NR_FIELDS = 6

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_SPREADSHEET_ID = '19hxttEYYDF6_eAUVDz2YRVzK_BSIeGScP8j_754dFk0'

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    for book_id in ['Cor']:
        parse_book(sheet, book_id)

def parse_book(sheet, book_id):
    range_name = book_id + "!A2:G"

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=range_name).execute()
    values = result.get('values', [])

    book_json = get_book_json(book_id, True)
    song_dict = {}
    for song in book_json['songs']:
        if book_id == 'Cor':
            song_dict[song['fname']] = song
        else:
            song_dict[int(song['number'])] = song

    print ('\n'.join(sorted([x for x in song_dict])))

    if not values:
        print('No data found.')
    else:
        for row in values:
            row += [u''] * MAX_NR_FIELDS
            # Print columns A and E, which correspond to indices 0 and 4.
            parse_song(book_id, row, song_dict)

def parse_song(book_id, row, song_dict):
    if book_id == 'Cor':
        song_nr = row[0]
    row = [normalize(x) for x in row]
    if book_id != 'Cor':
        song_nr = int(row[0])
    title = row[1]
    author = row[2]
    composer = row[3]
    original_title = row[4]
    year = row[5]
    references = row[6]

    if book_id == 'Cor' or song_nr in song_dict:
        song_json = song_dict[song_nr]
        song_json['author'] = author
        song_json['composer'] = composer
        song_json['original_title'] = original_title
        song_json['references'] = references

        if book_id == 'Cor':
            song_fname = song_json['fname']
            del song_json['fname']
        else:
            song_fname = get_song_fname(book_id, song_nr)
        save_song_json('./temp/{}/{}'.format(book_id, song_fname), song_json)
    else:
        print ('Song {} in {} not found\n', (song_nr, book_id))

def get_song_fname(book_id, song_nr):
    book_path = 'books/' + book_id
    files = [f for f in listdir(book_path) if isfile(join(book_path, f))]

    for fname in files:
        song_json = get_song_json(join(book_path, fname))
        if int(song_json['number']) == song_nr:
            return fname

if __name__ == '__main__':
    main()
