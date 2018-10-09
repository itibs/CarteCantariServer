#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
import json
from os import listdir
from os.path import isfile, join

BOOKS = ['CC', 'J', 'CT']

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/CarteCantari/books', methods=['GET'])
def get_books():
    return jsonify(
        [   {'id': 'CC', 'name': 'Cartea de Cantari'},
            {'id': 'J', 'name': 'Jubilate'},
            {'id': 'CT', 'name': 'Cartea de tineret'}])

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

def get_song_json(song_filename):
    with open(song_filename, 'rw') as f:
        lines = f.readlines()
        metalines = [l for l in lines if len(l) > 0 and l[0] == '@']
        lines = [l for l in lines if len(l) > 0 and l[0] != '@']
        lines = strip_lines(lines)

        song_json = {}
        for metaline in metalines:
            key, val = metaline.split(' ', 1)
            if key == '@Title':
                song_json['title'] = val.strip()
            elif key == '@Number':
                song_json['number'] = val.strip()
            else:
                print 'Unknown metadata song field: ' + key

        text = ''.join(lines)
        song_json['text'] = text
        return song_json

def get_book_json(book_id):
    book_path = 'books/' + book_id
    files = [f for f in listdir(book_path) if isfile(join(book_path, f))]
    book_json = {}
    book_json['id'] = book_id
    book_json['songs'] = []
    #return {'msg': [f for f in listdir(book_path)]}
    for fname in files:
        song_json = get_song_json(join(book_path, fname))
        book_json['songs'].append(song_json)

    return book_json

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
