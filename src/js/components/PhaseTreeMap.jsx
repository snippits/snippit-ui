import React from 'react';
import {connect} from 'react-redux';

import Highcharts from 'highcharts';
import ReactHighcharts from 'react-highcharts';
import extendTreemap from 'highcharts-treemap';
extendTreemap(ReactHighcharts.Highcharts);

// Related articles
// http://www.highcharts.com/blog/post/192-use-highcharts-to-create-charts-in-react/
// https://github.com/kirjs/react-highcharts/tree

const defaultOptions = {
    plotOptions: {
        series: {
            animation: {
                duration: 1000,
            },
        },
    },
    title: {
        text: 'Phase Tree Map of Execution Times',
    },
    subtitle: {
        text: '',
    },
    colorAxis: {
        minColor: '#FFFFFF',
        maxColor: Highcharts.getOptions().colors[0],
    },
    series: [],
    chart: {
        height: '400px',
    },
};

const defaultSeries = {
    type: 'treemap',
    layoutAlgorithm: 'squarified',
    allowDrillToNode: true,
    animationLimit: 500,
    dataLabels: {
        enabled: false,
    },
    levelIsConstant: false,
    levels: [{
        level: 1,
        dataLabels: {
            enabled: true,
            style: {fontSize: '15px'},
        },
        borderWidth: 3,
    }],
    data: [],
};

@connect((store) => {
    return {
        treemap: store.phase.treemap,
    };
})
export default class PhaseTreeMap extends React.Component {
    constructor() {
        super();

        this.config = {};
        this.phase_id = -1;
        this.last_selected_phase_id = -1;
        this.state = {
        };
    }

    // When the DOM is ready, create the chart.
    componentWillMount() {
        this.config = JSON.parse(JSON.stringify(defaultOptions));
        // Push a new series of our default config with deep copy
        let newSeries = JSON.parse(JSON.stringify(defaultSeries));
        // Assign data to the first series
        newSeries.data = [{name: 'No Phase ID specified', id: 'id_0', value: 1}];
        this.forceUpdate();

        this.config.series.push(newSeries);
    }

    render() {
        const {treemap} = this.props;
        console.log('PhaseTreeMap');

        if (treemap.error) {
            let chart = this.chart.getChart();
            chart.series[0].setData([{name: 'Profiling Result Not Found', id: 'id_0', value: 1}]);
        } else if (treemap.fetched) {
            let chart = this.chart.getChart();
            chart.series[0].setData(treemap.data);
        }

        return (
            <div className='col-md-12'>
                <ReactHighcharts
                    config={this.config}
                    isPureConfig={treemap.fetching}
                    ref={(ref) => this.chart = ref} />
            </div>
        );
    }
}
