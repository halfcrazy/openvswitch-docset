#!/usr/bin/env python
import sqlite3
import os
from bs4 import BeautifulSoup as bs
import requests

# reference https://github.com/iamaziz/emacs-dash/blob/master/emacs-gendoc2dash.py
docset_name = 'Openvswitch.docset'
output = docset_name + '/Contents/Resources/Documents'
doc_base_url = 'http://www.openvswitch.org/support/dist-docs/'

r = requests.get(doc_base_url)
soup = bs(r.text, 'html.parser')
# Open vSwitch 2.11.90 Documentation
# title = soup.title.string

# create directory
docpath = output + '/'
if not os.path.exists(docpath): os.makedirs(docpath)


def update_db(name, path):
    typ = 'Command'
    cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
    print('DB add >> name: %s, path: %s' % (name, path))


def add_docs():
    for link in filter(lambda x: x.text == 'HTML', soup.findAll('a')):
        # <a href="ovn-ctl.8.html">HTML</a>
        sub_path = link.get('href')
        url = doc_base_url + sub_path
        r = requests.get(url)
        print('download', sub_path)
        with open(docpath + sub_path, 'wb') as doc:
            doc.write(r.content)
        update_db(sub_path.replace('.html', ''), sub_path)


def add_infoplist():
    name = docset_name.split('.')[0]
    info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
           "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
           "<plist version=\"1.0\"> " \
           "<dict> " \
           "    <key>CFBundleIdentifier</key> " \
           "    <string>{0}</string> " \
           "    <key>CFBundleName</key> " \
           "    <string>{1}</string>" \
           "    <key>DocSetPlatformFamily</key>" \
           "    <string>{2}</string>" \
           "    <key>isDashDocset</key>" \
           "    <true/>" \
           "    <key>dashIndexFilePath</key>" \
           "    <string>{3}</string>" \
           "</dict>" \
           "</plist>".format(name, name, name, doc_base_url)
    open(docset_name + '/Contents/Info.plist', 'w').write(info)


if __name__ == '__main__':
    db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
    cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # start
    add_docs()
    add_infoplist()

    # commit and close db
    db.commit()
    db.close()

