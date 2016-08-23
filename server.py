#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, \
     request, send_from_directory, abort
import xapers as X
import argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--xapers-root',
                    help="Xapers root directory", default="~/.xapers/docs")
parser.add_argument('--host', help="Host", default="0.0.0.0")
parser.add_argument('-p', '--port', help="Port", default=5000, type=int)

args = parser.parse_args()
args.xapers_root = os.path.join(os.path.expanduser(args.xapers_root), '')
print "Args:", args
app = Flask(__name__)

def queryDB(q, limit=0):
    return X.Database(args.xapers_root).search(q, limit)

@app.route("/id/<int:id>")
def file_by_id(id):
    res = queryDB('id:'+str(id), 1)
    if len(res) == 0: abort(404)
    path = res[0].get_files()[0]
    path = '{0:0>10}/{1}'.format(id, path)
    print "SERVING PATH", args.xapers_root + path
    return send_from_directory(args.xapers_root+'/', path)

@app.route("/")
@app.route("/search")
def search():
    keywords = request.args.get('q', '')
    limit = int(request.args.get('l', 0))
    res = queryDB(keywords, limit)
    res = [ {'id': item.get_docid(),
             'matchp': item.matchp,
             'bib': item.get_bibdata(),
             'path': item.get_fullpaths()[0].decode('utf-8')}
           for item in res]
    
    return render_template("search_results.html", res=res)

if __name__ == "__main__":
    from eventlet import wsgi
    import eventlet
    wsgi.server(eventlet.listen((args.host, args.port)), app)
    #app.run()
