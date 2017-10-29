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


# input: a node and its id
# output: a dict containing the node's attributes
def serialize_course(course, c_id):
    return {
        'title': course['title'],
        'code': course['code'],
        'resume': course['resume'],
        'id': c_id
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
    results = db.run("MATCH (c:Course) RETURN ID(c) as node_id, c.code as code, c.title as course") # get all node records from the db in a list

    nodes = [] # all nodes
    rels = [] # all relations (edges)
    neighs_dict = {} # neighboring information
    for record in results:
        nodes.append({"node_id": record["node_id"], "code": record["code"], "title": record["course"], "label": "course"})
        neighs_dict[record["node_id"]] = set()

    relationships = db.run("MATCH (c1:Course) -[r]->(c2:Course) RETURN ID(c1) as source, ID(c2) as target")
    for rel in relationships:
        index_c1 = rel['source']
        index_c2 = rel['target']
        rels.append({"source": index_c1, "target": index_c2})
        neighs_dict[index_c1].add(index_c2)
        neighs_dict[index_c2].add(index_c1)

    # remove duplicates
    neighs_dict = {k: list(v) for k, v in neighs_dict.items()}


    return Response(dumps({"nodes": nodes, "links": rels, "neighbors_dict": neighs_dict}),
                    mimetype="application/json")

# return search bar results
@app.route("/search")
def get_search():
    try:
        q = request.args["q"]
    except KeyError:
        return []
    else:
        db = get_db()
        results = db.run("MATCH (c:Course) WHERE c.title =~ {title} RETURN c as c, id(c) as c_id", {"title": "(?i).*" + q + ".*"})
        return Response(dumps([serialize_course(record['c'], record['c_id']) for record in results]),
                        mimetype="application/json")

# returns the neighbors of a single node given as argument
@app.route("/get_neighbors")
def get_neighbors():
    try:
        nodeId = request.args["q"]
    except KeyError:
        print("keyerror")
        return []
    else:
        # return all the neighbors of the query node
        db = get_db()
        neighbors = db.run("MATCH (n)-[*1..1]-(m) WHERE ID(n)="+nodeId+" RETURN distinct ID(m) as id")
        return Response(dumps([{'neigh':neigh['id']} for neigh in neighbors]), mimetype="application/json")



if __name__ == '__main__':
    app.run(debug=True, port=8080)
