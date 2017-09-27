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

def serialize_movie(movie):
    return {
        'id': movie['id'],
        'title': movie['title'],
        'summary': movie['summary'],
        'released': movie['released'],
        'duration': movie['duration'],
        'rated': movie['rated'],
        'tagline': movie['tagline']
    }

def serialize_cast(cast):
    return {
        'name': cast[0],
        'job': cast[1],
        'role': cast[2]
    }

@app.route("/graph")
def get_graph():
    db = get_db()
    #results = db.run("MATCH (m:Movie)<-[:ACTED_IN]-(a:Person) "
    #         "RETURN m.title as movie, collect(a.name) as cast "
    #         "LIMIT {limit}", {"limit": request.args.get("limit", 1000)})
    #results = db.run("MATCH (p:Person) RETURN p.name as name")
    results = db.run("MATCH (c:Course) RETURN c.title as course")
    nodes = []
    rels = []
    i = 0
    for record in results:
        i = i + 1
        #nodes.append({"title": record["movie"], "label": "movie"})
        #nodes.append({"title": record["name"], "label": "name"})
        nodes.append({"title": record["course"], "label": "course"})
        # if i < 700:
            # rels.append({"source":i, "target":i+10})
        #target = i
        #i += 1

    relationships = db.run("MATCH (c1:Course) -[r]->(c2:Course) RETURN c1.title as source, c2.title as target")
    for rel in relationships:
        #print(rel["source"])
        index_c1 = nodes.index({"title": rel["source"], "label": "course"})
        index_c2 = nodes.index({"title": rel["target"], "label": "course"})
        rels.append({"source": index_c1, "target": index_c2})
    i = 0
    print("hello", file=sys.stderr)
    for record1 in results:
        print("hello2", file=sys.stderr)
        i = i + 1
        j = 0
        '''
        for record2 in results:
            j = j + 1
            if True:
                rels.append({"source": i, "target": j})
                print(i, file=sys.stderr)

        '''
        '''
        for name in record['cast']:
            actor = {"title": name, "label": "actor"}
            try:
                source = nodes.index(actor)
            except ValueError:
                nodes.append(actor)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
            '''
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
        results = db.run("MATCH (movie:Movie) "
                 "WHERE movie.title =~ {title} "
                 "RETURN movie", {"title": "(?i).*" + q + ".*"}
        )
        return Response(dumps([serialize_movie(record['movie']) for record in results]),
                        mimetype="application/json")


@app.route("/movie/<title>")
def get_movie(title):
    db = get_db()
    results = db.run("MATCH (movie:Movie {title:{title}}) "
             "OPTIONAL MATCH (movie)<-[r]-(person:Person) "
             "RETURN movie.title as title,"
             "collect([person.name, "
             "         head(split(lower(type(r)), '_')), r.roles]) as cast "
             "LIMIT 1", {"title": title})

    result = results.single();
    return Response(dumps({"title": result['title'],
                           "cast": [serialize_cast(member)
                                    for member in result['cast']]}),
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(debug=True, port=8080)
