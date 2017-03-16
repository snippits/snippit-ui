import React from "react";
import { connect } from "react-redux"

import Highcharts from "highcharts";
import ReactHighcharts from 'react-highcharts';
import HighchartsTreemap from 'highcharts/modules/treemap';
HighchartsTreemap(ReactHighcharts.Highcharts);

import { fetchTreemap } from "../actions/phaseActions.js"

// Related articles
// http://www.highcharts.com/blog/post/192-use-highcharts-to-create-charts-in-react/
// https://github.com/kirjs/react-highcharts/tree

const default_options = {
    plotOptions: {
        series: {
            animation: {
                duration: 1000,
            },
        }
    },
    title: {
        text: 'Phase Tree Map of Execution Times'
    },
    subtitle: {
        text: ''
    },
    colorAxis: {
        minColor: '#FFFFFF',
        maxColor: Highcharts.getOptions().colors[0]
    },
    series: [],
    chart: {
        height: '400px',
    },
};

const default_series = {
    type: 'treemap',
    layoutAlgorithm: 'squarified',
    allowDrillToNode: true,
    animationLimit: 500,
    dataLabels: {
        enabled: false
    },
    levelIsConstant: false,
    levels: [{
        level: 1,
        dataLabels: {
            enabled: true,
            style: {fontSize: "15px"}
        },
        borderWidth: 3
    }],
    data: []
};

@connect((store) => {
  return {
    treemap: store.phase.treemap,
  };
})
export default class PhaseTreeMap extends React.Component {
    constructor() {
        super()

        this.config = {};
        this.phase_id = -1;
        this.last_selected_phase_id = -1;
        this.state = {
        };
    }

    loadPhaseTreemap(phase_id, cb) {
        setTimeout(function() {
            // Don't send request if this request is out-dated
            if (this.phase_id == phase_id) {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        cb(JSON.parse(this.responseText));
                    }
                    else {
                        cb([{name: "Profiling result not found", id: "id_0", value: 1}]);
                    }
                };
                var link = "output/phase-treemap-" + phase_id;
                xhttp.open("GET", link + "?_=" + new Date().getTime(), true);
                xhttp.send();
            }
        }.bind(this), 30);
    }

    loadTreemap(phase_id) {
        this.loadPhaseTreemap(phase_id, function(data) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData(data);
        }.bind(this));
    }

    // When the DOM is ready, create the chart.
    componentDidMount() {
        this.config = JSON.parse(JSON.stringify(default_options));
        // Push a new series of our default config with deep copy
        var new_series = JSON.parse(JSON.stringify(default_series));
        // Assign data to the first series
        new_series.data = [{name: "Profiling result not found", id: "id_0", value: 1}];
        this.forceUpdate();

        this.config.series.push(new_series);
    }

    render() {
        const { treemap } = this.props;
        this.phase_id = this.props.selected_phase_id;
        if (this.props.selected_phase_id != this.last_selected_phase_id) {
            this.props.dispatch(fetchTreemap(this.phase_id));
            // this.loadTreemap(this.props.selected_phase_id);
            this.last_selected_phase_id = this.phase_id;
        }

        if (treemap.fetched) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData(treemap.data);
        }

        // Always render when parent state changes
        return (
            <div class="col-md-12">
                <ReactHighcharts config={this.config} isPureConfig={treemap.fetching} ref="chart"></ReactHighcharts>
            </div>
        );
    }
}
