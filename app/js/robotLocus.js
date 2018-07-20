const WIDTH = 800;
const HEIGHT = 800;
const MARGIN = 10;
const TICKS = 10;

import setUpdatetimePicker from "./datetimePicker";

class Locus {
    constructor() {
        this.svg = d3.select("svg#robotLocus")
                     .attr("width", WIDTH)
                     .attr("height", HEIGHT);
        this.dataset = [];
        this.setAxes();
    }

    setAxes() {
        this.xScale = d3.scaleLinear()
                        .domain([-1.5, 1.5])
                        .range([MARGIN, WIDTH - MARGIN]);
        this.yScale = d3.scaleLinear()
                        .domain([-1.5, 1.5])
                        .range([HEIGHT - MARGIN, MARGIN]);

        const axisx = d3.axisBottom(this.xScale)
                        .ticks(TICKS)
                        .tickFormat(d => d != 0 ? String(d) : "");
        const axisy = d3.axisLeft(this.yScale)
                        .ticks(TICKS)
                        .tickFormat(d => d != 0 ? String(d) : "");

        this.svg.append("g")
                .attr("transform", "translate(" + 0 + "," + HEIGHT / 2 + ")")
                .call(axisx);

        this.svg.append("g")
                .attr("transform", "translate(" + WIDTH / 2 + "," + 0 + ")")
                .call(axisy);
    }

    plot() {
        this.svg.append("path")
                .datum(this.dataset)
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 2)
                .attr("d", d3.line().x(d => this.xScale(d.x))
                                    .y(d => this.yScale(d.y)));

        this.svg.append("g")
                .selectAll("circle")
                .data(this.dataset)
                .enter()
                .append("circle")
                .attr("cx", d => this.xScale(d.x))
                .attr("cy", d => this.yScale(d.y))
                .attr("fill", "steelblue")
                .attr("r", 1);
    }
}

const show = (locus) => {
    const st = $("input#st_datetime_value").val();
    const et = $("input#et_datetime_value").val();

    let i = 0;
    function append() {
        locus.dataset.push({x: Math.cos(i * Math.PI/16), y: Math.sin(i * Math.PI/16)});
        locus.plot();
        i++;
        if (i <= 32) {
            setTimeout(append, 100);
        }
    }
    setTimeout(append, 100);
}

$(() => {
    setUpdatetimePicker();

    const locus = new Locus();
    $("button#show_button").on("click", (event) => { show(locus); });
});
