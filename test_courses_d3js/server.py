#!/usr/bin/env python
from __future__ import print_function # In python 2.7
import sys, copy
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

# input: an empty ajdacency list and the db handle
# output: a list of all the edges and a list of dictionnary, each one being an adjacency list (source noce -> edgeID) for a distinct edge type
def get_edges_and_ajd_lists(initial_list, db, directional_edges=True):
    adjacency_lists = dict() # will contain all the adjacency lists
    adjacency_lists['ALL_EDGES'] = initial_list # this ajdacency list contains all relations with no distinction on the edge type
    for edge_type in get_edge_types(db):
        adjacency_lists[edge_type] = copy.deepcopy(initial_list)
    rels = [] # all relations (edges)
    relationships = db.run("MATCH (c1:Course)-[r]->(c2:Course) RETURN ID(c1) as source, ID(c2) as target, ID(r) as edge_id, TYPE(r) as edge_type")
    for rel in relationships:
        rel_type = rel['edge_type']
        index_source = rel['source']
        index_target = rel['target']
        edge_id = rel['edge_id']
        rels.append({"source": index_source, "target": index_target, "edge_id": edge_id, "edge_type": rel_type})
        adjacency_lists[rel_type][index_source].add(edge_id)
        adjacency_lists['ALL_EDGES'][index_source].add(edge_id)
        #if not directional_edges:
        #    adjacency_list[index_target].add(edge_id)

    for key, ajd_list in adjacency_lists.items():
        adjacency_lists[key] = {k: list(v) for k, v in ajd_list.items()} # turn set to list (set => no duplicates)
    return [adjacency_lists, rels]

 # returns a list containing all distinct edge types as strings
def get_edge_types(db):
    results = db.run("MATCH (a)-[r]->(b) RETURN distinct(type(r)) as type")
    return [record['type'] for record in results]

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()

@app.route("/")
def get_index():
    return app.send_static_file('index.html')

# sends a JSON to the front-end with all the nodes and the edgesets
@app.route("/graph")
def get_graph():
    db = get_db()
    results = db.run("MATCH (c:Course) RETURN ID(c) as node_id, c.code as code, c.title as course") # get all node records from the db in a list

    nodes = [] # all nodes
    empty_ajd_list = {} # neighboring information
    for record in results:
        nodes.append({"node_id": record["node_id"], "code": record["code"], "title": record["course"], "label": "course"})
        empty_ajd_list[record["node_id"]] = set() # initialize the adjacency list with empty sets

    [adjacency_lists, rels] = get_edges_and_ajd_lists(empty_ajd_list, db)

    return Response(dumps({"nodes": nodes, "links": rels, "adjacency_lists": adjacency_lists}),
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
    #app.run(debug=False, host='192.168.1.111', port=8080)
    app.run(debug=True, port=8080)
