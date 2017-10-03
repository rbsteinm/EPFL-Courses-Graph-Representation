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


def serialize_course(course):
    return {
        'title': course['title'],
        'code': course['code'],
        'resume': course['resume']
}

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


# displays the graph when the page is loaded
@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (c:Course) RETURN ID(c) as node_id, c.code as code, c.title as course")
    nodes = []
    rels = []
    index_dict = {} # contains matching between neo4j's node ids and node indexes for the front end
    node_index = 0
    for record in results:
        nodes.append({"node_id": record["node_id"], "code": record["code"], "title": record["course"], "label": "course", "index" : node_index})
        assert(not record["node_id"] in index_dict)
        index_dict[record["node_id"]] = node_index
        node_index += 1

    relationships = db.run("MATCH (c1:Course) -[r]->(c2:Course) RETURN ID(c1) as source, ID(c2) as target")
    for rel in relationships:

        index_c1 = index_dict[rel["source"]]
        index_c2 = index_dict[rel["target"]]
        rels.append({"source": index_c1, "target": index_c2})

    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")

@app.route("/search")
def get_search():
    try:
        q = request.args["q"]
    except KeyError:
        return []
    else:
        db = get_db()
        results = db.run("MATCH (c:Course) "
                 "WHERE c.title =~ {title} "
                 "RETURN c", {"title": "(?i).*" + q + ".*"}
        )
        return Response(dumps([serialize_course(record['c']) for record in results]),
                        mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True, port=8080)
