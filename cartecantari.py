# -*- coding: utf-8 -*-
#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
import json
from os import listdir
from os.path import isfile, join
import io
import pdb

BOOKS = {
    'CC': 'Cartea de Cântari',
    'J': 'Jubilate',
    'Cor': 'Cântari Cor',
    'CT': 'Cartea de Tineret',
    'A': 'Altele'
}

app = Flask(__name__, static_url_path='/static')

META_FIELDS = [u'title', u'number', u'author', u'composer', u'original_title', u'references', u'tag', u'pitch']

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/bible.yes', methods=['GET'])
def get_VDC():
    return app.send_static_file('ro-cornilescu-correct.yes')

@app.route('/CarteCantari/books', methods=['GET'])
def get_books():
    return jsonify(
        [   {'id': 'CC', 'name': 'Cartea de Cantari'},
            {'id': 'J', 'name': 'Jubilate'},
            {'id': 'Cor', 'name': 'Cantari Cor'},
            {'id': 'CT', 'name': 'Cartea de tineret'},
            {'id': 'A', 'name': 'Altele'}])

@app.route('/CarteCantari/books/v2', methods=['GET'])
def get_books_with_song_summaries():
    books = [get_book_json(book_id, get_fname=False, get_summary=True) for book_id in BOOKS]
    for book in books:
        book['title'] = BOOKS[book['id']]
        book['song_summaries'] = book['songs']
        del book['songs']
    return jsonify(books)

@app.route('/CarteCantari/books/<string:book_id>', methods=['GET'])
def get_task(book_id):
    if book_id in BOOKS:
        print 'Book ' + book_id
        book_json = get_book_json(book_id)
        return jsonify(book_json)
    else:
        abort(404)

def strip_lines(lines):
    i = 0
    while i < len(lines) and lines[i] == '\n':
        i += 1
    if i != len(lines):
        return lines[i:]
    return []

def get_song_json(song_filename, get_fname=False, get_summary=False):
    with open(song_filename, 'rw') as f:
        lines = f.readlines()
        metalines = [l for l in lines if len(l) > 0 and l[0] == '@']
        lines = [l for l in lines if len(l) > 0 and l[0] != '@']
        lines = strip_lines(lines)

        song_json = {}
        for metaline in metalines:
            key, val = metaline.split(' ', 1)
            meta_field = key[1:].lower()
            if meta_field in META_FIELDS:
                if meta_field == 'tag':
                    if 'tags' in song_json:
                        song_json['tags'].append(val.strip())
                    else:
                        song_json['tags'] = [val.strip()]
                else:
                    song_json[meta_field] = val.strip()
            else:
                # print 'Unknown metadata song field: ' + key + str((song_filename, val))
                pass

        if get_summary == False:
            text = ''.join(lines)
            song_json['text'] = text

        if get_fname:
            if '/' in song_filename:
                idx = song_filename.rfind('/')
                song_filename = song_filename[idx+1:]
            song_json['fname'] = song_filename
        return song_json

def get_book_json(book_id, get_fname=False, get_summary=False):
    book_path = 'books/' + book_id
    files = [f for f in listdir(book_path) if isfile(join(book_path, f))]
    book_json = {}
    book_json['id'] = book_id
    book_json['songs'] = []

    for fname in files:
        song_json = get_song_json(join(book_path, fname), get_fname, get_summary)
        book_json['songs'].append(song_json)

    return book_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

def save_song_json(song_filename, song_json):
    with io.open(song_filename, 'w', encoding='utf-8') as f:
        for meta_field in META_FIELDS:
            if meta_field in song_json and song_json[meta_field] != '':
                f.write(u'@{} {}\n'.format(meta_field.title(), touni(song_json[meta_field])))
        if 'tags' in song_json:
            for tag in song_json['tags']:
                f.write(u'@Tag {}\n'.format(touni(tag)))
        f.write(u'\n')
        f.write(touni(song_json['text']))

def touni(s):
    if isinstance(s, str):
        return s.decode('utf-8')
    return s
