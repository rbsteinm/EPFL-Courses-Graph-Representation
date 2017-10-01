#!/usr/bin/env python
from __future__ import print_function # In python 2.7
import sys
from json import dumps

from flask import Flask, g, Response, request

from neo4j.v1 import GraphDatabase, basic_auth, ResultError

app = Flask(__name__, static_url_path='/static/')
# driver = GraphDatabase.driver('bolt://localhost')
driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "pikachu74"))
# basic auth with: driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("<user>", "<pwd>"))

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()

@app.route("/")
def get_index():
    return app.send_static_file('index.html')


@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (c:Course) RETURN c.title as course")
    nodes = []
    rels = []
    for record in results:
        nodes.append({"title": record["course"], "label": "course"})

    relationships = db.run("MATCH (c1:Course) -[r]->(c2:Course) RETURN c1.title as source, c2.title as target")
    for rel in relationships:
        #print(rel["source"])
        index_c1 = nodes.index({"title": rel["source"], "label": "course"})
        index_c2 = nodes.index({"title": rel["target"], "label": "course"})
        rels.append({"source": index_c1, "target": index_c2})

    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True, port=8080)
