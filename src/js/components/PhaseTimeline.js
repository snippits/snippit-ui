import React from "react";
import { connect } from "react-redux"

import Highcharts from "highcharts";
import ReactHighstock from 'react-highcharts/ReactHighstock'
import SimilaritySlider from '../components/SimilaritySlider'

import { fetchTimeline } from "../actions/phaseActions.js"

// Related articles
// http://www.highcharts.com/blog/post/192-use-highcharts-to-create-charts-in-react/
// https://github.com/kirjs/react-highcharts/tree

const default_options = {
    plotOptions: {
        series: {
            animation: {
                duration: 2000,
            },
            allowPointSelect: true,
        }
    },
    rangeSelector: {
        allButtonsEnabled: true,
        selected: 4,
        buttons: [{
            type: 'millisecond',
            count: 2000,
            text: 'ms'
        }, {
            type: 'second',
            count: 10,
            text: '1s'
        }, {
            type: 'minute',
            count: 1,
            text: '1M'
        }, {
            type: 'hour',
            count: 1,
            text: '1H'
        }, {
            type: 'all',
            text: 'All'
        }],
        inputDateFormat: '%H:%M:%S.%L',
        inputEditDateFormat: '%H:%M:%S.%L',
    },

    title: {
        text: 'Phase ID Timeline',
    },

    yAxis: {
        allowDecimals: false,
        title: {
            text: 'Phase ID',
            style: {fontSize: "25px"},
        },
    },

    chart: {
        height: '400px',
    },

    scrollbar: {
        liveRedraw: false
    },
    series: [],
};

const default_series = {
    name: 'Phase ID',
    marker: {
        enabled: null, // auto
        radius: 3,
        lineWidth: 1,
    },
    tooltip: {
        valueDecimals: 0,
    },
    linecap:"round",
    allowPointSelect: true,
    showCheckbox: false,
    selected: true,
    data: [],
    point:{events:{}},
    dataGrouping: {
        enabled: false,
    },
};

@connect((store) => {
  return {
    timeline: store.phase.timeline,
  };
})
export default class PhaseTimeline extends React.Component {

    constructor() {
        super()

        this.config = {};
        this.last_similarity_threshold = 90;
        this.state = {
            similarity_threshold: 90,
        };
    }

    loadPhaseHistory(similarity_threshold, cb) {
        setTimeout(function() {
            // Don't send request if this request is out-dated
            if (this.state.similarity_threshold == similarity_threshold) {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        cb(JSON.parse(this.responseText));
                    }
                };
                similarity_threshold = parseInt(similarity_threshold / 10)
                var link = "output/phase-history-" + similarity_threshold;
                xhttp.open("GET", link + ".json?_=" + new Date().getTime(), true);
                xhttp.send();
            }
        }.bind(this), 30);
    }

    loadHistory(similarity_threshold) {
        this.loadPhaseHistory(similarity_threshold, function(data) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData(data);
        }.bind(this));
    }

    // When the DOM is ready, create the chart.
    componentDidMount() {
        this.config = JSON.parse(JSON.stringify(default_options));

        // Push a new series of our default config with deep copy
        var new_series = JSON.parse(JSON.stringify(default_series));
        // Change marker line color (not series line color)
        new_series.marker.lineColor = '#FFFFFF';
        // Assign data to the first series
        new_series.data = [];
        // Assign mouse event to the first series
        new_series.point.events.select = this.props.select_event;

        this.config.series.push(new_series);
        this.forceUpdate();

        this.props.dispatch(fetchTimeline(this.state.similarity_threshold));

        // this.loadHistory(this.state.similarity_threshold);
    }

    handle_slider_change(value) {
        if (this.last_similarity_threshold != value) {
            this.props.dispatch(fetchTimeline(value));
            // this.loadHistory(value);
        }
        this.last_similarity_threshold = value;
        this.setState({similarity_threshold: value});
    }

    render() {
        console.log("timeline");
        const { timeline } = this.props;

        if (timeline.fetched && 
            this.state.similarity_threshold == timeline.similarity_threshold) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData(timeline.data);
        }

        return (
            <div class="col-md-12">
                <SimilaritySlider set_change={this.handle_slider_change.bind(this)} similarity_threshold={this.state.similarity_threshold} />
                <ReactHighstock config={this.config} isPureConfig={true} ref="chart"></ReactHighstock>
            </div>
        );
    }
}
