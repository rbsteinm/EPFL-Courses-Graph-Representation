// This file contains the original Javascript code
// The production has been retro-compiled for ES-2015 to fix compatibility issues and is located in frontend/main_ES5.js

const NODE_COLOR = "rgba(145, 145, 145, 1)";
const EDGE_COLOR = "rgba(145, 145, 145, 0.8)";
const SELECTED_EDGE_COLOR = "rgba(0, 0, 0, 0.8)";
const BACKGROUND_NODE_COLOR = "rgba(142,136,130, 0.1)";
const BACKGROUND_EDGE_COLOR = "rgb(229,229,229)";

const HIGHLIGHT_DEPTH = 2;
const BATCH_SIZE = 50;
const SHOW_LABELS_THRESHOLD = 0.5;
const NODE_SIZE = 13;
let current_node_size = NODE_SIZE;
const MAX_NODE_SIZE = 75;
const FONT_SIZE = 12;
const ZOOM_CONSTRAIN = [0.05, 2.5];
const HIDE_ARROWHEADS_THRESHOLD = 0.25;
//const HIGHLIGHT_COLORS = ['#5C5C5C', '#454545', '#2E2E2E', '#171717', '#000000'];
const HIGHLIGHT_COLORS = ['rgb(180, 180, 180)', 'rgb(100, 100, 100)', 'rgb(0, 0, 0)'];
//const HIGHLIGHT_COLORS = ['#90BECE', '#67B3CE', '#29A2CE'];

let nodes = {};
let edges = {};
let NODE_SELECTION = [];
let EDGE_SELECTION = [];
let course_descriptions = {};
let course_sections = {};
let adjacency_list = {};
let drawing_timer;
let drawing_complete = true;
let show_labels = true;
let arrowheads_visible = true;
let ZOOMED = false;

// _______________________________________________________ DOM ELEMENTS _______________________________________________________


// define width/height as the svg container dimensions
let width = document.getElementsByClassName('svg-container')[0].clientWidth;
let height = document.getElementsByClassName('svg-container')[0].clientHeight;

// create the SVG element that will contain the nodes and edges
let svg = d3.select("div#graph").append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .classed("svg-content", true);
let g = svg.append("g");

// triangle at the end of edges (arrowheads)
svg.append('defs')
.append('marker')
.attrs({'id':'arrowhead',
    'viewBox':'-0 -5 10 10',
    'refX':29,
    'refY':0,
    'orient':'auto',
    'markerWidth':0.5 * NODE_SIZE,
    'markerHeight':0.5 * NODE_SIZE,
    'xoverflow':'visible'})
.append('svg:path')
.attr('d', 'M 0,-5 L 10 ,0 L 0,5')
.attr('fill', EDGE_COLOR)
.style('stroke','none');


// handle zoom events on the svg
let zoom_handler = d3.zoom()
    .scaleExtent(ZOOM_CONSTRAIN)
    .on("start", function(){
        return zoomBegin();
    })
    .on("end", function(){
        return zoomEnd(width, height, d3.event.transform);
    })
    .on("zoom", function(){
        return zoomed(width, height, d3.event.transform);
    });

svg.call(zoom_handler);

// no double click zoom
d3.select("svg").on("dblclick.zoom", null);

// called when the window is resized (on tablet, rotated for example)
window.addEventListener("resize", function(){
    // recompute width and height of the screen
    width = document.getElementsByClassName('svg-container')[0].clientWidth;
    height = document.getElementsByClassName('svg-container')[0].clientHeight;
    // refresh the graph
    zoomBegin();
    zoomed(width, height, d3.zoomTransform(svg.node()));
    zoomEnd(width, height, d3.zoomTransform(svg.node()));
});

// When the background is clicked, clear the current selection
d3.select("div#graph").on("click", function(){
    clear_selection(false);
    hide_infopanel();
    show_node_labels(d3.zoomTransform(svg.node()));
    // refresh the graph
    zoomBegin();
    zoomed(width, height, d3.zoomTransform(svg.node()));
    zoomEnd(width, height, d3.zoomTransform(svg.node()));
    // clear search box
    hide_searchbox();
});


// _______________________________________________________ IMPORT AND INIT _______________________________________________________


// this function imports the data from a .gexf file
// the advantage of gexf file is that we can use Gephi's algorithm to have a nice pre-defined layout
// a callback function displays the data once it's loaded
function import_data(path, display_callback){
    var graph = gexf.fetch(path);

    // import nodes data
    graph.nodes.forEach(function(n){
        nodes['nid_' + n.id] = {
            'x': n.viz.position.x,
            'y': n.viz.position.y,
            'title': n.attributes.subjectname,
            'id': 'nid_' + n.id
        };
    });

    // import edges data
    graph.edges.forEach(function(e){
        edges['eid_' + e.id] = {
            'source': 'nid_' + e.source,
            'target': 'nid_' + e.target,
            'x1': graph.nodes.filter(node => node.id == e.source)[0].viz.position.x,
            'y1': graph.nodes.filter(node => node.id == e.source)[0].viz.position.y,
            'x2': graph.nodes.filter(node => node.id == e.target)[0].viz.position.x,
            'y2': graph.nodes.filter(node => node.id == e.target)[0].viz.position.y,
            'id': 'eid_' + e.id,
            'type': e.label
        }
    });

    // fill the adjacency list
    Object.values(edges).forEach(function(e){
        if(!adjacency_list[e.source]) adjacency_list[e.source] = [];
        adjacency_list[(e.source)].push(e.id);
    });

    // callback function that displays the data when loading is done
    display_callback();
}

// this function creates a circle for each course and an edge for each relationship
// it is called as a callback of the import_data method
function display_graph(){
    // initial scaling and position of the graph with a mind-blowing futuristic avant-gardiste animation
    svg.call(zoom_handler.transform, translate_to_center(60));
    svg.transition().delay(1500).duration(5000).call(zoom_handler.transform, translate_to_center(0.07)).ease(d3.easeBack);
    // draw the edges
    g.selectAll(".link")
        .data(Object.values(edges)).enter()
        .append("line")
        .attr("x1", function(d) {return d.x1;})
        .attr("y1", function(d) {return d.y1;})
        .attr("x2", function(d) {return d.x2;})
        .attr("y2", function(d) {return d.y2;})
        .attr("id", function(d) {return d.id;})
        .attr("class", function(d) {
            return (d.type == 'baseline') ? 'link': 'link indicative_link';
        })
        .style('stroke', EDGE_COLOR)
        .attr('marker-end','url(#arrowhead)');

    // draw the nodes
    g.selectAll(".node")
        .data(Object.values(nodes)).enter()
        .append("circle")
        .attr("cx", function(d) {return d.x;})
        .attr("cy", function(d) {return d.y;})
        .attr("class", "node")
        .attr("id", d => d.id)
        .style('fill', NODE_COLOR)
        .on("click", function(d) {
            on_click_node(d.id);
        });

    // add text above nodes
    g.selectAll("text")
        .data(Object.values(nodes), function(d){return d.id;})
        .enter()
        .append('text')
        .attr('x', function(d){return d.x+5;})
        .attr('y', function(d){return d.y-16;})
        .attr('id', function(d){return 'title_' + d.id;})
        .attr('class', 'node_title')
        .text(function(d){ return d.title});
}

// import course descriptions in a dictionary nodeID -> description
function import_descriptions(){
    d3.tsv("./frontend/data/descriptions.csv")
        .row(function(row){
            course_descriptions['nid_' + row.SubjectID] = row.Summary_EN;
        })
        .get(function(err, rows) {
            if (err) return console.error(err);
        });
}

// import course sections in a dictionary nodeID -> sections
// a course can be given to multiple sections
function import_sections(){
    d3.tsv("./frontend/data/sections.csv")
        .row(function(row){
            course_sections['nid_' + row.SubjectID] = row.sections.split('|');
        })
        .get(function(err, rows) {
            if (err) return console.error(err);
        });
}


// data loading and initial graph display
import_data('./frontend/data/data4.gexf', function(){display_graph();});
import_descriptions();
import_sections();


// _______________________________________________________ NODES AND EDGES METHODS _______________________________________________________


// this function is called when a node is clicked
function on_click_node(node_id){
    // highlight the node and its neighbors
    highlight_selection(node_id);

    // fill the information panel with the node's information
    fill_infopanel(node_id);
    show_infopanel();

    // update visible node labels to show only those of selected courses
    hide_node_labels();
    show_node_labels(d3.zoomTransform(svg.node()));

    // only the node is clicked, not the background
    event.stopPropagation();

    // animated movement
    svg.transition().duration(1500).call(zoom_handler.transform, translate_to(node_id, 0.3));
}

// returns the size each node should have according the the current zoom level
// each time there is a zoom event, the nodes must be resized so that they keep the same size visually
function get_node_size(scale_factor){
    return Math.min(MAX_NODE_SIZE, (NODE_SIZE/scale_factor));
}

// same as get_node_size, but for the width of the edged
function get_line_width(scale_factor){
    return (1.0/((scale_factor))).toFixed(2);
}

// same again, but for the font size of node labels
function get_label_font_size(scale_factor){
    return (FONT_SIZE/scale_factor);
}

// returns the coordinates after a transformation (zoom, pan)
function get_new_coordinates(x, y, transf){
    let x1 = x * transf.k + transf.x,
    y1 = y * transf.k + transf.y;
    return [x1, y1];
}

// does this node appear on the screen with the current scale/translate values?
// this allows to only resize/draw/... nodes that are visible to gain computation time
function node_is_visible(node, width, height, transf){
    let x, y;
    //let radius = parseInt(g.select('#'+node.id).style('r'));
    // hardcoded radius approximation for performance reasons
    let radius = 100;
    [x, y] = get_new_coordinates(node.x, node.y, transf);
    return (x+radius) > 0 && (x-radius) < width && (y+radius) > 0 && (y-radius) < height;
}

// does this edge appear on the screen with the current scale/translate values?
// this algorithm basically checks if the edge intersects at least on on the SVG borders
// if it's the case, then the edge is visible in the viewport
function edge_is_visible(edge, width, height, transf){
    let x1, x2, y1, y2;
    [x1, y1] = get_new_coordinates(edge.x1 ,edge.y1, transf);
    [x2, y2] = get_new_coordinates(edge.x2 ,edge.y2, transf);
    let new_edge = [x1, y1, x2, y2];
    let left_border = [0, 0, 0, height];
    let top_border = [0, 0, width, 0];
    let right_border = [width, 0, width, height];
    let bottom_border = [0, height, width, height];

    // both endpoints are inside the box
    if(x1 > 0 && x1 < width && y1 > 0 && y1 < height && x2 > 0 && x2 < width && y2 > 0 && y2 < height){
        return true;
    }
    // the edge intersects at least one of the borders
    if(line_intersects(new_edge, top_border) || line_intersects(new_edge, left_border) || line_intersects(new_edge, right_border) || line_intersects(new_edge, bottom_border)){
        return true;
    }
    return false;
}

// are the two segments intersecting at some point?
function line_intersects(segment1, segment2) {
    [p0_x, p0_y, p1_x, p1_y] = segment1;
    [p2_x, p2_y, p3_x, p3_y] = segment2;
    var s1_x, s1_y, s2_x, s2_y;
    s1_x = p1_x - p0_x;
    s1_y = p1_y - p0_y;
    s2_x = p3_x - p2_x;
    s2_y = p3_y - p2_y;

    var s, t;
    s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y);
    t = ( s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y);

    return (s >= 0 && s <= 1 && t >= 0 && t <= 1);
}

// recursive BFS algorithm to highlight the given node and its neighbors and their neighbors
// is_source: true if the node is the selected node (root node)
// distance: highlight all nodes that are d hops away from the root, for all d <= distance
// already_seen: the nodes that were already visited and highlightd by the algorithm (to avoid highlighting a node twice)
function highlight_selection(node_id, is_source=true, distance=HIGHLIGHT_DEPTH, already_seen=[]){

    if(is_source){
        clear_selection(true);
        already_seen.push(node_id);
    }
    highlight_node(node_id, distance);
    NODE_SELECTION.push(node_id);

    // also highlight neighbors (and the edge that links to each neighbor)
    if(distance > 0){
        if(!adjacency_list[node_id]) return;
        let adjacent_edges = adjacency_list[node_id].map(edge_id => get_edge_by_id(edge_id));
        adjacent_edges.forEach(function(edge){
            highlight_edge(edge, distance);
            EDGE_SELECTION.push(edge);
        });
        let unvisited_nodes = adjacent_edges.map(edge => edge.target).filter(nid => !already_seen.includes(nid));
        unvisited_nodes.forEach(nid => already_seen.push(nid));
        unvisited_nodes.forEach(nid =>  highlight_selection(nid, false, distance-1, already_seen));
    }
}

// highlights the given node with opacity proportional to the root distance
function highlight_node(node_id, distance_to_leaf){
    d3.select('circle#'+node_id).transition().duration(1000).delay(get_highlight_delay(distance_to_leaf)).style('fill', HIGHLIGHT_COLORS[distance_to_leaf]);
    //d3.select('circle#'+node_id).style('visibility', 'visible');

}

// highlights an edge
function highlight_edge(edge, distance_to_leaf){
    let selected_edge = d3.select('#' + edge.id);
    selected_edge.style('stroke', HIGHLIGHT_COLORS[distance_to_leaf-1]);
    // use transition so that the edge becomes visible exactly when its target node has finished to draw
    selected_edge.transition().duration(0).delay(get_highlight_delay(distance_to_leaf-1)+1000).style('visibility', 'visible');
    // having an opacity transition is nice on a computer, but too costly => laggy on the tablet
    //selected_edge.style('opacity', 0).transition().duration(0).delay(get_highlight_delay(distance_to_leaf-1)).style('opacity', 1);
}

// when a node is selected, the BFS algorithm is ran and its neighborhood nodes are displayed after a delay
// the bigger the distance to the source node, the bigger the delay
// this function computes the delay before showing a node/edge given its distance to the leaf level
// of the highlighted tree
function get_highlight_delay(distance_to_leaf){
    return d3.scaleLinear().domain([HIGHLIGHT_DEPTH, 0]).range([0, 2000])(distance_to_leaf);
}

// returns the DOM node object given its node ID
function get_node_by_id(id){
    return d3.select('#'+id).data()[0];
}

//input: edge id
// output: the edge's data
function get_edge_by_id(id){
    return d3.select('#'+id).data()[0];
}

// clears the highlighting and all node/edge selection
// new_selection: true if a new node was clicked, false if the background was clicked
// the transition() are here to kill any ongoing transition on the nodes/links
function clear_selection(new_selection=false){
    NODE_SELECTION = [];
    EDGE_SELECTION = [];
    if(new_selection){
        d3.selectAll('.node').transition().style('fill', BACKGROUND_NODE_COLOR);
        //d3.selectAll('.link').style('stroke', BACKGROUND_EDGE_COLOR);
        //d3.selectAll('.node').style('visibility', 'hidden');
        d3.selectAll('.link').transition().style('visibility', 'hidden');
    }
    else{
        d3.selectAll('.node').transition().style('fill', NODE_COLOR);
        d3.selectAll('.link').style('stroke', EDGE_COLOR);
        d3.selectAll('.node').style('visibility', 'visible');
        d3.selectAll('.link').transition().style('visibility', 'visible');
    }
}


// _______________________________________________________ ZOOM AND DRAG EVENTS _______________________________________________________


// This code is executed everytime the page is zoomed
// it's executed at each single zoom event, so a lot of time in a single scroll/drag
// It dinamically resizes the nodes, but only if they are visible to reduce computation time
function zoomed(width, height, transform){
    // hide all links
    d3.selectAll('.link').style('display', 'none');
    // hide node labels
    hide_node_labels();
    // apply the transformation
    g.attr("transform", transform);
    // update node size
    const radius = get_node_size(transform.k);
    current_node_size = radius;
    d3.selectAll('.node').filter(node => node_is_visible(node, width, height, transform)).style("r", radius);
    // was there been a drag or a zoom or was it only a click?
    // if this method is executed, it means the SVG has moved
    // thus, redrawing the edges and labels will be necessary and the end of the zoom event
    ZOOMED = true;
    //console.log('zommed');
}

// this function is called at the beginning of any zoom or drag event
// if a new drawing occurs while the current drawing is unfinished, 
// the current drawing is interrupted and the new one is launched immediately
function zoomBegin(){
    // Stop the timer (if it's initialized)
    if(drawing_timer){
        console.log('stopped timer')
        drawing_timer.stop();
    }
}

// this function is called at the end of any zoom or drag event
// it launches the redrawing of visible edges
// the visible edges are drawn by batches of size BATCH_SIZE
function zoomEnd(width, height, transform){
    // check if the graph has been moved
    // this allows to distinguish a click and a drag event (the click event does not go through the 'zoomed()' method)
    if(ZOOMED){
        redraw_edges(width, height, transform);
        show_node_labels(transform);
        show_hide_arrowheads(transform);
        ZOOMED = false;
    }
}

// this function draws a single batch of edges
// batch: an array of edge IDs to draw
// line_width: the stroke width of the edges
function draw_edge_batch(batch, line_width){
    g.selectAll('.link')
        .data(batch, function(e){return e.id;})
        //.style('stroke-width', 0)
        //.transition().duration(200)
        .style("stroke-width", line_width)
        .style('display', 'block');
}

// this function draws back the visible edges after any zoom or drag
// it interrupts the drawing timer if and when the drawing is completed
// note that the timer can also be interrupted by a more recent zoom event in 'zoomBegin()'
// the visible edges are drawn by batches of size BATCH_SIZE
function redraw_edges(width, height, transform){
    drawing_complete = false;

    const line_width = get_line_width(transform.k);
    let batch_number = 0;
    let visible_edges = d3.selectAll('.link').filter(edge => edge_is_visible(edge, width, height, transform)).data();
    // if there is a selection, only draw selected edges
    if(EDGE_SELECTION.length > 0) visible_edges = visible_edges.filter(edge => EDGE_SELECTION.includes(edge));
    // make sure to end the timer in case it's running
    if(drawing_timer) drawing_timer.stop();
    // this timer calls its parameter function over and over again until it is stopped
    drawing_timer = d3.timer(function(){
        let batch = visible_edges.splice(0, Math.min(BATCH_SIZE, visible_edges.length));
        draw_edge_batch(batch, line_width);
        batch_number += 1;
        // stop the timer if all edges have been drawn
        if(visible_edges.length == 0){
            console.log('drawing complete');
            drawing_timer.stop();
            drawing_complete = true;
        }
    }, 0);
}

// transforms the graph so that the node with id nid is
// at the center of the viewport
// called when a new node is selected (on_click_node())
function translate_to(nid, scale_factor) {
    let node = nodes[nid];
    let [x, y] = get_new_coordinates(node.x, node.y, d3.zoomTransform(svg.node()));
  return d3.zoomIdentity
      .translate(width/2, (height - parseInt(d3.select('#infopanel').style('height')))/2)
      .scale(scale_factor)
      .translate(-node.x, -node.y);
}

// translates the graph to the center of the screen
function translate_to_center(scale_factor){    
    return d3.zoomIdentity
      .translate(width/2, height/2)
      .scale(scale_factor)
}


// _______________________________________________________ NODE LABELS AND ARROWHEADS _______________________________________________________


// shows the labels of the nodes if the zoom threshold is reached
// only shows labels of visible nodes
function show_node_labels(transform){
    // is the zoom threshold reached?
    if(transform.k > SHOW_LABELS_THRESHOLD){
        let font_size = get_label_font_size(transform.k);

        // filter out the nodes that do not appear on the screen
        let visible_nodes = d3.selectAll('.node')
        .filter(node => node_is_visible(node, width, height, transform))
        .data();

        // if there is a selection, only show labels of selected nodes
        if(NODE_SELECTION.length > 0) visible_nodes = visible_nodes.filter(node => NODE_SELECTION.includes(node.id));

        // display the label for each visible node
        d3.selectAll('.node_title')
            .data(visible_nodes, function(d){return d.id;})
            .style('display', 'block')
            .style('font-size', font_size);
    }
}

// hides all the node labels
function hide_node_labels(){
    g.selectAll('.node_title').style('display', 'none');
}

// at a certain unzooming threshold, the arrowheads are hidden
// to avoid the graph to be messy
function show_hide_arrowheads(transform){
    // to zoomed out, don't display arrowheads
    if(transform.k < HIDE_ARROWHEADS_THRESHOLD && arrowheads_visible){
        g.selectAll('.link').attr('marker-end','none');
        arrowheads_visible = false;
    }
    // display arrowheads
    else if(transform.k >= HIDE_ARROWHEADS_THRESHOLD && !arrowheads_visible){
        g.selectAll('.link').attr('marker-end','url(#arrowhead)');
        arrowheads_visible = true;
    }
}


// _______________________________________________________ INFOPANEL _______________________________________________________


// show the information panel for the selected course at the bottom of the screen
function show_infopanel(){
    d3.select('#infopanel').style('opacity', 0).transition().duration(500).style('opacity', 1).style('pointer-events', 'auto');
}

function hide_infopanel(){
    d3.select('#infopanel').transition().duration(500).style('opacity', 0).style('pointer-events', 'none');
}

// fills the information panel with info about course with id nid
function fill_infopanel(nid){
    let infopanel = d3.select('#infopanel');
    // empty the infopanel
    infopanel.selectAll('*').remove();
    // title
    infopanel.append('div')
        .append('strong')
        .text(nodes[nid].title);
    // description
    infopanel.append('div').text(course_descriptions[nid]);
    infopanel.append('br');
    // sections
    if(course_sections[nid]){
        let text = '<strong style="">This course is thaught to: </strong> <br/>';
        course_sections[nid].forEach(function(s){
            text += s + '<br/>';
        });
        infopanel.append('div').style('font-size', '13px').html(text);
    }
    infopanel.append('br');
    // related courses
    if(adjacency_list[nid]){
        infopanel.append('div').style('font-size', '13px').style('font-weight', 'bold').text('Related courses:');
        let related_courses = adjacency_list[nid].map(eid => edges[eid].target);
        related_courses.forEach(function(nid){
            infopanel.append('span')
                .text(nodes[nid].title)
                .attr('class', 'related_course')
                .on('click', function(){
                    on_click_node(nid);
                    g.select('circle#' + nid).style('stroke-width', '0px');
                })
                .on('mouseover', function(){
                    d3.select(this)
                        .style('border-color', 'rgba(100, 100, 100, 1)')
                        .style('cursor', 'pointer');
                    g.select('circle#' + nid).style('stroke', 'black').style('stroke-width', current_node_size/6 + 'px');
                })
                .on('mouseout', function(){
                    d3.select(this)
                        .style('border-color', 'transparent')
                        .style('cursor', 'default');
                        g.select('circle#' + nid).style('stroke-width', '0px');
                })
        });
    }
}


// _______________________________________________________ SEARCHBOX _______________________________________________________


// fills the search panel results
// called each time a key is pressed in the searchbox
function search(query){
    d3.select('#search_results_container').style('border-style', 'solid');
    // empty query => no result
    if(query == ''){
        d3.selectAll('.search_results_cell').remove();
        return;
    }
    // the courses that contain the query on their title
    let result_nids = Object.values(nodes).filter(node => String(node.title).toLowerCase().includes(query.toLowerCase()));
    // keep only the first 10
    result_nids = result_nids.slice(0,10);

    let cells = d3.select('#search_results_container')
        .selectAll('.search_results_cell')
        .data(result_nids, function(d){return d.id;});


    cells.enter()
        .append('div')
        .attr('class', 'search_results_cell')
        .on('click', function(d){
            hide_searchbox();
            on_click_node(d.id);
        })
        .on('mouseover', function(d){
            d3.select(this)
                .style('background-color', 'rgba(180, 180, 180, 0.2)')
                .style('cursor', 'pointer');
        })
        .on('mouseout', function(d){
            d3.select(this)
                .style('background-color', 'transparent')
                .style('cursor', 'default');
        })
        .text(function(d){return d.title;});

    cells.exit().remove();
}

// hide search results
function hide_searchbox(){
    d3.select('#search_results_container').style('border-style', 'hidden');
    d3.selectAll('.search_results_cell').remove();
    d3.select('#searchbox').property('value', '');
}