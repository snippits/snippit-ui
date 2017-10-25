import React from 'react';
import {connect} from 'react-redux';

import SimilaritySlider from '../components/SimilaritySlider';
import ReactHighstock from 'react-highcharts/ReactHighstock';
import extendExporting from 'highcharts-exporting';
extendExporting(ReactHighstock.Highcharts);

import {fetchTimeline, setSelectedPhase} from '../actions/phaseActions.js';

// Related articles
// http://www.highcharts.com/blog/post/192-use-highcharts-to-create-charts-in-react/
// https://github.com/kirjs/react-highcharts/tree

const defaultOptions = {
    plotOptions: {
        series: {
            cursor: 'pointer',
            animation: {
                duration: 2000,
            },
            allowPointSelect: true,
        },
    },
    rangeSelector: {
        allButtonsEnabled: true,
        selected: 4,
        buttons: [{
            type: 'millisecond',
            count: 2000,
            text: 'ms',
        }, {
            type: 'second',
            count: 10,
            text: '1s',
        }, {
            type: 'minute',
            count: 1,
            text: '1M',
        }, {
            type: 'hour',
            count: 1,
            text: '1H',
        }, {
            type: 'all',
            text: 'All',
        }],
        inputDateFormat: '%H:%M:%S.%L',
        inputEditDateFormat: '%H:%M:%S.%L',
    },

    title: {
        text: 'Phase ID Timeline',
    },

    xAxis: {
        ordinal: false,
    },

    yAxis: {
        allowDecimals: false,
        title: {
            text: 'Phase ID',
            style: {fontSize: '25px'},
        },
    },

    chart: {
        height: '400px',
    },

    scrollbar: {
        liveRedraw: false,
    },
    series: [],
};

const defaultSeries = {
    name: 'Phase ID',
    marker: {
        enabled: null, // auto
        radius: 3,
        lineWidth: 1,
    },
    tooltip: {
        valueDecimals: 0,
    },
    linecap: 'round',
    allowPointSelect: true,
    showCheckbox: false,
    selected: true,
    data: [],
    point: {events: {}},
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
        super();

        this.config = {};
        this.state = {
            similarityThreshold: 0,
        };

        // This binding is necessary to make `this` work in the callback
        this.handleSliderChange = this.handleSliderChange.bind(this);
    }

    // When the DOM is ready, create the chart.
    componentWillMount() {
        this.config = JSON.parse(JSON.stringify(defaultOptions));

        // Push a new series of our default config with deep copy
        let newSeries = JSON.parse(JSON.stringify(defaultSeries));
        // Change marker line color (not series line color)
        newSeries.marker.lineColor = '#FFFFFF';
        // Assign data to the first series
        newSeries.data = [];
        // Assign mouse event to the first series
        newSeries.point.events.select = this.selectEvent.bind(this);
        // Assign inital value of data series
        this.config.series.push(newSeries);

        // Set initial value if it's not assigned
        let similarityThreshold = this.props.similarityThreshold;
        this.setState({similarityThreshold: similarityThreshold});
        this.props.dispatch(fetchTimeline(similarityThreshold));
    }

    selectEvent(event) {
        let selectedItem = event.target['y'];
        // console.log(selectedItem)
        if (selectedItem !== undefined) {
            this.props.dispatch(setSelectedPhase(selectedItem, this.state.similarityThreshold));
            return true;
        }
        return false;
    }

    handleSliderChange(value) {
        this.setState({similarityThreshold: value});
        this.props.dispatch(fetchTimeline(value));
    }

    render() {
        console.log('PhaseTimeline');
        const {timeline} = this.props;

        if (timeline.error) {
            let chart = this.chart.getChart();
            chart.showLoading('Timeline Result Not Found');
        } else if (timeline.fetching) {
            let chart = this.chart.getChart();
            chart.showLoading('Loading data from server...');
        } else if (timeline.fetched) {
            let chart = this.chart.getChart();
            chart.series[0].setData(timeline.data);
            chart.hideLoading();
        }

        return (
            <div className='col-md-12'>
                <SimilaritySlider
                    onChange={this.handleSliderChange}
                    value={this.state.similarityThreshold} />
                <ReactHighstock
                    config={this.config}
                    isPureConfig={true}
                    ref={(ref) => this.chart = ref} />
            </div>
        );
    }
}
