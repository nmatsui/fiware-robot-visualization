'use strict';

const WIDTH = 800;
const HEIGHT = 800;
const MARGIN = 10;
const TICKS = 10;
const DELTA = 100;

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
                .attr("data-type", "plotpath")
                .attr("fill", "none")
                .attr("stroke", "steelblue")
                .attr("stroke-width", 2)
                .attr("d", d3.line().x(d => this.xScale(d.x))
                                    .y(d => this.yScale(d.y)));

        this.svg.append("g")
                .attr("data-type", "plotcircle")
                .selectAll("circle")
                .data(this.dataset)
                .enter()
                .append("circle")
                .attr("cx", d => this.xScale(d.x))
                .attr("cy", d => this.yScale(d.y))
                .attr("fill", "steelblue")
                .attr("r", 1);
    }

    clear() {
        this.dataset = [];
        this.svg.selectAll("path[data-type=plotpath]")
                .data(this.dataset)
                .exit()
                .remove();
        this.svg.selectAll("g[data-type=plotcircle]")
                .data(this.dataset)
                .exit()
                .remove();
    }

    show() {
        toggleButtons(false);
        this.clear();

        const st = $("input#st_datetime_value").val();
        const et = $("input#et_datetime_value").val();

        $.ajax({
            type: "GET",
            url: "/positions/",
            data: {
                st: st,
                et: et
            },
            dataType: 'json'
        }).done((data) => {
            let i = 0;
            let append = () => {
                this.dataset.push(data[i]);
                this.plot();
                i++;
                if (i < data.length) {
                    this.timer = setTimeout(append, DELTA);
                } else {
                    toggleButtons(true);
                }
            }
            this.timer = setTimeout(append, DELTA);
        }).fail(() => {
            console.error("can't get the robot positions");
            toggleButtons(true);
        });
    }

    stop() {
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
        toggleButtons(true);
    }
}

const toggleButtons = (can_render) => {
    if (can_render) {
        $("div#not_rendering").show();
        $("div#rendering").hide();
    } else {
        $("div#not_rendering").hide();
        $("div#rendering").show();
    }
};

$(() => {
    toggleButtons(true);
    setUpdatetimePicker();

    const locus = new Locus();
    $("button#show_button").on("click", event => locus.show());
    $("button#clear_button").on("click", event => locus.clear());
    $("button#stop_button").on("click", event => locus.stop());
});
