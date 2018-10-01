'use strict';

const WIDTH = 700;
const HEIGHT = 700;
const MARGIN = 10;
const TICKS = 10;
const DELTA = 100;
const INIT_DOMAIN = 0.1

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
                        .domain([-1 * INIT_DOMAIN, INIT_DOMAIN])
                        .range([MARGIN, WIDTH - MARGIN]);
        this.yScale = d3.scaleLinear()
                        .domain([-1 * INIT_DOMAIN, INIT_DOMAIN])
                        .range([HEIGHT - MARGIN, MARGIN]);

        this.xAxis = d3.axisBottom(this.xScale)
                        .ticks(TICKS)
                        .tickFormat(d => d != 0 ? String(d) : "");
        this.yAxis = d3.axisLeft(this.yScale)
                        .ticks(TICKS)
                        .tickFormat(d => d != 0 ? String(d) : "");

        this.svg.append("g")
                .attr("data-type", "xAxis")
                .attr("transform", "translate(" + 0 + "," + HEIGHT / 2 + ")")
                .call(this.xAxis);

        this.svg.append("g")
                .attr("data-type", "yAxis")
                .attr("transform", "translate(" + WIDTH / 2 + "," + 0 + ")")
                .call(this.yAxis);
    }

    updateAxes(d) {
        this.xScale.domain([-1 * d, d]);
        this.yScale.domain([-1 * d, d]);
        this.svg.select("g[data-type=xAxis]").call(this.xAxis);
        this.svg.select("g[data-type=yAxis]").call(this.yAxis);
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
        this.updateAxes(INIT_DOMAIN);

        $("div#point_num").text("");
        $("div#time").text("");
        $("div#pos_x").text("");
        $("div#pos_y").text("");
        $("div#pos_theta").text("");
    }

    show() {
        toggleButtons(false);
        this.clear();

        const bearer = $("input#bearer").val();
        const path = $("input#path").val();
        const st = $("input#st_datetime_value").val();
        const et = $("input#et_datetime_value").val();

        $.ajax({
            type: "GET",
            url: path,
            headers: {
                'Authorization': 'Bearer ' + bearer
            },
            data: {
                st: formatISO8601(new Date(st)),
                et: formatISO8601(new Date(et))
            },
            dataType: 'json'
        }).done((data) => {
            $("p#point_num").text("0/" + String(data.length) + " points");
            if (data.length > 0) {
                let maxX = Math.max(...data.map(d => d.x).map(x => x ? Math.abs(x) : Number.MIN_VALUE))
                let maxCeilX = Math.ceil(maxX * 10) / 10;

                let maxY = Math.max(...data.map(d => d.y).map(y => y ? Math.abs(y) : Number.MIN_VALUE))
                let maxCeilY = Math.ceil(maxY * 10) / 10;

                this.updateAxes(Math.max(maxCeilX, maxCeilY));

                let i = 0;
                let prev_x = Number.MIN_VALUE;
                let prev_y = Number.MIN_VALUE;
                let append = () => {
                    if (data[i].x != null && data[i].y != null && (data[i].x != prev_x || data[i].y != prev_y)) {
                        this.dataset.push({
                            x: data[i].x,
                            y: data[i].y
                        });
                        this.plot();
                        prev_x = data[i].x
                        prev_y = data[i].y
                    }

                    $("div#point_num").text("point : " + String(i + 1) + "/" + String(data.length));
                    $("div#time").text("time : " + String(data[i].time));
                    if (data[i].x != null) {
                        $("div#pos_x").text("x : " + String(data[i].x));
                    }
                    if (data[i].y != null) {
                        $("div#pos_y").text("y : " + String(data[i].y));
                    }
                    if (data[i].theta != null) {
                        $("div#pos_theta").text("θ : " + String(data[i].theta));
                    }

                    i++;
                    if (i < data.length) {
                        this.timer = setTimeout(append, DELTA);
                    } else {
                        toggleButtons(true);
                    }
                }
                this.timer = setTimeout(append, DELTA);
            } else {
                toggleButtons(true);
            }
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

const formatISO8601 = (date) => {
    let o = date.getTimezoneOffset() / -60;
    let offset = ((0 < o) ? '+' : '-') + ('00' + Math.abs(o)).substr(-2) + ':00';

    return [
        [
            date.getFullYear(),
            ('00' + (date.getMonth() + 1)).substr(-2),
            ('00' + date.getDate()).substr(-2)
        ].join('-'),
        'T',
        [
            ('00' + date.getHours()).substr(-2),
            ('00' + date.getMinutes()).substr(-2),
            ('00' + date.getSeconds()).substr(-2)
        ].join(':'),
        offset
    ].join('');
};

$(() => {
    toggleButtons(true);
    setUpdatetimePicker();

    const locus = new Locus();
    $("button#show_button").on("click", event => locus.show());
    $("button#clear_button").on("click", event => locus.clear());
    $("button#stop_button").on("click", event => locus.stop());
});
