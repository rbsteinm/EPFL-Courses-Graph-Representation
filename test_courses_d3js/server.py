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
    return {'title': course['title'], 'code': course['code'], 'resume': course['resume'], 'id': c_id}

def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db

def get_edges_and_ajd_list(initial_list, db, edge_type, directional_edges=True):
    adjacency_list = initial_list # neighboring information
    rels = [] # all relations (edges)
    relationships = db.run("MATCH (c1:Course)-[r:"+ edge_type + "]->(c2:Course) RETURN ID(c1) as source, ID(c2) as target, ID(r) as edge_id")
    for rel in relationships:
        index_source = rel['source']
        index_target = rel['target']
        edge_id = rel['edge_id']
        rels.append({"source": index_source, "target": index_target, "edge_id": edge_id})
        adjacency_list[index_source].add(edge_id)
        if not directional_edges:
            adjacency_list[index_target].add(edge_id)

    adjacency_list = {k: list(v) for k, v in adjacency_list.items()} # turn set to list (set => no duplicates)
    return [adjacency_list, rels]

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
    #rels = [] # all relations (edges)
    empty_ajd_list = {} # neighboring information
    for record in results:
        nodes.append({"node_id": record["node_id"], "code": record["code"], "title": record["course"], "label": "course"})
        empty_ajd_list[record["node_id"]] = set() # initialize the adjacency list with empty sets

    [adjacency_list, rels] = get_edges_and_ajd_list(empty_ajd_list, db, "REQUIRE_OBL", False)

    return Response(dumps({"nodes": nodes, "links": rels, "adjacency_list": adjacency_list}),
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
    #app.run(debug=False, host='128.179.152.254', port=8080)
    app.run(debug=True, port=8080)
