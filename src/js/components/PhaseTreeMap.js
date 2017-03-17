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

    // When the DOM is ready, create the chart.
    componentWillMount() {
        this.config = JSON.parse(JSON.stringify(default_options));
        // Push a new series of our default config with deep copy
        var new_series = JSON.parse(JSON.stringify(default_series));
        // Assign data to the first series
        new_series.data = [{name: "No Phase ID specified", id: "id_0", value: 1}];
        this.forceUpdate();

        this.config.series.push(new_series);
    }

    render() {
        const { treemap } = this.props;
        console.log("PhaseTreeMap");

        if (treemap.error) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData([{name: "Profiling Result Not Found", id: "id_0", value: 1}]);
        } else if (treemap.fetched) {
            let chart = this.refs.chart.getChart();
            chart.series[0].setData(treemap.data);
        }

        return (
            <div class="col-md-12">
                <ReactHighcharts config={this.config} isPureConfig={treemap.fetching} ref="chart"></ReactHighcharts>
            </div>
        );
    }
}
