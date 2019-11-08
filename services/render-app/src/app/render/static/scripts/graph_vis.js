var namespaceColorList = {
    occ: "#FF6666",
    omg: "rgb(185, 15, 34)",
    rdf: "rgb(128, 69, 151)",
    oop: "blue"

};


var getColor = function (name) {
    return namespaceColorList[name];
};



//graphvis functions 
function filterNodesById(nodes, id) {
    return nodes.filter(function (n) { return n.id === id; });
}

function filterNodesByType(nodes, value) {
    return nodes.filter(function (n) { return n.type === value; });
}

function triplesToGraph(triples) {

    svg.html("");
    //Graph
    var graph = { nodes: [], links: [], triples: [] };

    //Initial Graph from triples
    triples.forEach(function (triple) {
        var subjId = triple.subject;
        var predId = triple.predicate;
        var objId = triple.object;

        var subjNode = filterNodesById(graph.nodes, subjId)[0];
        var objNode = filterNodesById(graph.nodes, objId)[0];

        if (subjNode == null) {
            subjNode = { id: subjId, label: subjId, weight: 1, type: "node" };
            graph.nodes.push(subjNode);
        }

        if (objNode == null) {
            objNode = { id: objId, label: objId, weight: 1, type: "node" };
            graph.nodes.push(objNode);
        }

        var predNode = { id: predId, label: predId, weight: 1, type: "pred" };
        graph.nodes.push(predNode);

        var blankLabel = "";

        graph.links.push({ source: subjNode, target: predNode, predicate: blankLabel, weight: 1 });
        graph.links.push({ source: predNode, target: objNode, predicate: blankLabel, weight: 1 });

        graph.triples.push({ s: subjNode, p: predNode, o: objNode });

    });

    return graph;
}


function update(graph) {

    // ==================== Add Marker ====================
    svg.append("svg:defs").selectAll("marker")
        .data(["end"])
        .enter().append("svg:marker")
        .attr("id", String)
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 30)
        .attr("refY", -0.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("svg:polyline")
        .attr("points", "0,-5 10,0 0,5")
        
        ;

    // ==================== Add Links ====================
    var links = svg.selectAll(".link")
        .data(graph.triples)
        .enter()
        .append("path")
        .attr("marker-end", "url(#end)")
        .attr("class", "link")
        .style("stroke", function (d) {return getNodeColor(d.p);})


        ;

    // ==================== Add Link Names =====================
    var linkTexts = svg.selectAll(".link-text")
        .data(graph.triples)
        .enter()
        .append("text")
        .attr("class", "link-text")
        .text(function (d) { return d.p.label; })
        .style("fill", function (d) {return getNodeColor(d.p);})
        ;

    //linkTexts.append("title")
    //		.text(function(d) { return d.predicate; });

    // ==================== Add Node Names =====================
    var nodeTexts = svg.selectAll(".node-text")
        .data(filterNodesByType(graph.nodes, "node"))
        .enter()
        .append("text")
        .attr("class", "node-text")
        .text(function (d) { return d.label; })
        .style("fill", function (d) {return getNodeColor(d);})
        ;

    //nodeTexts.append("title")
    //		.text(function(d) { return d.label; });

    // ==================== Add Node =====================
    var nodes = svg.selectAll(".node")
        .data(filterNodesByType(graph.nodes, "node"))
        .enter()
        .append("circle")
        .attr("class", "node")
        .attr("r", 8)
        .call(force.drag)
        .style("fill", function (d) {return getNodeColor(d);})
        ;//nodes

    // ==================== Force ====================
    force.on("tick", function () {
        nodes
            .attr("cx", function (d) { return d.x; })
            .attr("cy", function (d) { return d.y; })
            ;

        links
            .attr("d", function (d) {
                return "M" + d.s.x + "," + d.s.y
                    + "S" + d.p.x + "," + d.p.y
                    + " " + d.o.x + "," + d.o.y;
            })
            ;

        nodeTexts
            .attr("x", function (d) { return d.x + 12; })
            .attr("y", function (d) { return d.y + 3; })
            ;


        linkTexts
            .attr("x", function (d) { return 4 + (d.s.x + d.p.x + d.o.x) / 3; })
            .attr("y", function (d) { return 4 + (d.s.y + d.p.y + d.o.y) / 3; })
            ;
    });

    // ==================== Run ====================
    force
        .nodes(graph.nodes)
        .links(graph.links)
        .charge(-500)
        .linkDistance(50)
        .start()
        ;
}

// dic erstellen mit key value dann den jeweiligen color wert finden für nodes und text ergänzen
function getNodeColor(d){
    var color ="grey";
    Object.keys(namespaceColorList).forEach(function(item){
        if(d.label.startsWith(item)){
            color= namespaceColorList[item];    
        }
    })

    if (!isNaN(d.label)){
        color="green";
    }
    if(!(clickedItem=="")){
    if(d.label.includes(clickedItem)){
        color="black";
    }
}

    return color; 
}


function getWidth() {
    divElement =document.getElementById("graphContainer");
    // return divElement.clientWidth ;
    return Math.max(
        document.body.scrollWidth,
        document.documentElement.scrollWidth,
        document.body.offsetWidth,
        document.documentElement.offsetWidth,
        document.documentElement.clientWidth
    )-40;
}

//   var triples = {{subPredObj|safe}};
svgElement = document.getElementById("svg-body")

CANVAS_WIDTH= svgElement.clientWidth;

        
var force = d3.layout.force().size([CANVAS_WIDTH, 400]);
function redraw() {
    svg.attr("transform",
        "translate(" + d3.event.translate + ")"
        + " scale(" + d3.event.scale + ")");
}

var svg = d3.select("#svg-body")
    .append("svg")
    .attr("width", getWidth() / 2)
    .attr("height", 400)
    .attr("pointer-events", "all")
    .call(d3.behavior.zoom().on("zoom", redraw))
    .append('svg:g');


var force = d3.layout.force().size([getWidth() / 2, 400]);

var drag = force.drag()
    .on("dragstart", function (d) {
        d3.event.sourceEvent.stopPropagation();
    });
