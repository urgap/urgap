//
// Author Christian Fufezan
// Inspired by http://bl.ocks.org/mbostock/1153292

window.onload = function drawAllGraphs() {
    network_ids.forEach(drawGraph);
};

function drawGraph(nid) {
    const network = window[nid];

    const nonRedundantNodes = getNonRedundantNodes(network.nodes);
    const maxProcessingTime = d3.max(nonRedundantNodes, d => d.processing_time);

    network.nodes = nonRedundantNodes;

    const height = 700;
    const arrowHead = getArrowHeadConfig();
    const nodeDefs = getNodeDefinitions();

    const toolTip = d3.select("body").append("div")
        .attr("class", "tooltip-urgap-node")
        .style("opacity", 0);

    const svg = d3.select(`#${nid}`).append("svg")
        .attr("class", "svg-content")
        .attr("width", "100%")
        .attr("height", height);

    const width = parseInt(svg.style("width"));
    const radius = 15;

    setupDefinitions(svg, arrowHead, radius);

    const simulation = d3.forceSimulation(network.nodes)
        .force("center", d3.forceCenter(width / 2, height / 2))
        .force("links", d3.forceLink(network.links).id(d => d.name))
        .force('charge', d3.forceManyBody().strength(-70))
        .force('collision', d3.forceCollide().radius(radius * 2))
        .on("tick", tickActions);

    const g = svg.append("g").attr("class", "everything");

    const link = g.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(network.links)
        .enter().append("line")
        .style("stroke", d => arrowHead[d.type].color)
        .attr("stroke-width", 4)
        .attr('marker-end', d => `url(#${arrowHead[d.type].arrowId})`);

    const node = g.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(network.nodes)
        .enter().append("circle")
        .attr("r", radius)
        .attr("stroke", d => nodeDefs[d.id].stroke)
        .attr("stroke-width", d => nodeDefs[d.id].stroke_width)
        .attr("fill", d => circleColour(d, maxProcessingTime))
        .on('mouseover', handleMouseOver(toolTip))
        .on('mouseout', handleMouseOut(toolTip));

    const dragHandler = d3.drag()
        .on("start", dragStart(simulation))
        .on("drag", drag)
        .on("end", dragEnd(simulation));

    dragHandler(node);

    const zoomHandler = d3.zoom().on("zoom", zoomActions(g));
    zoomHandler(svg);

    function tickActions() {
        node.attr("cx", d => d.x).attr("cy", d => d.y);
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
    }
}

function getNonRedundantNodes(nodes) {
    const nodeNames = new Set();
    return nodes.filter(node => {
        if (!nodeNames.has(node.name)) {
            nodeNames.add(node.name);
            return true;
        }
        return false;
    });
}

function getArrowHeadConfig() {
    return {
        incoming: { color: "#af8dc3", arrowId: "arrowhead_incoming" },
        outgoing: { color: "#7fbf7b", arrowId: "arrowhead_outgoing" }
    };
}

function getNodeDefinitions() {
    return {
        process: { stroke_width: 3, stroke: "white", fill: "Will be computed by processing time" },
        data: { stroke_width: 1, stroke: "black", fill: "#ccc" }
    };
}

function setupDefinitions(svg, arrowHead, radius) {
    svg.append('defs')
        .selectAll("marker")
        .data(Object.keys(arrowHead))
        .enter().append("marker")
        .attr('id', d => arrowHead[d].arrowId)
        .attr('viewBox', '0 0 10 10')
        .attr('refX', 7 + radius)
        .attr('refY', 5)
        .attr('orient', 'auto')
        .attr('markerWidth', 3)
        .attr('markerHeight', 3)
        .attr('xoverflow', 'visible')
        .append('svg:path')
        .attr('d', 'M 0 0 L 10 5 L 0 10 z')
        .attr('fill', d => arrowHead[d].color)
        .style('stroke', 'none');
}

function circleColour(d, maxProcessingTime) {
    if (d.id === "process") {
        return d3.interpolateMagma(d.processing_time / maxProcessingTime);
    } else {
        return getNodeDefinitions()[d.id].fill;
    }
}

function handleMouseOver(toolTip) {
    return function(d) {
        d3.select(this).transition().duration(50).attr('opacity', '.75');
        toolTip.transition().duration(50).style('opacity', '1');
        toolTip.html(formatToolTip(d))
            .style("left", `${d3.event.pageX + 10}px`)
            .style("top", `${d3.event.pageY - 15}px`);
    };
}

function handleMouseOut(toolTip) {
    return function(d) {
        d3.select(this).transition().duration(50).attr('opacity', '1');
        toolTip.transition().duration(50).style('opacity', '0');
    };
}

function formatToolTip(d) {
    return d.id === "process" ? `${d.name}<br> Processing time (s):${d.processing_time}` : d.name;
}

function dragStart(simulation) {
    return function(d) {
        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    };
}

function drag(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragEnd(simulation) {
    return function(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    };
}

function zoomActions(g) {
    return function() {
        g.attr("transform", d3.event.transform);
    };
}
