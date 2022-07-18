//
// Author Christian Fufezan
// Inspired by http://bl.ocks.org/mbostock/1153292

};



        .attr("class", "svg-content")
        .attr("width", "100%")



        .force('charge', d3.forceManyBody().strength(-70))
        .force('collision', d3.forceCollide().radius(radius * 2))
        .on("tick", tickActions);


        .attr("class", "links")
        .selectAll("line")
        .data(network.links)
        .enter().append("line")
        .attr("stroke-width", 4)

        .attr("class", "nodes")
        .selectAll("circle")
        .data(network.nodes)
        .attr("r", radius)







    }

        if (!d3.event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;


        if (!d3.event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
