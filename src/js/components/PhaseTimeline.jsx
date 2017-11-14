import React from 'react';
import {connect} from 'react-redux';

import SimilaritySlider from '../components/SimilaritySlider';
import ReactHighstock from 'react-highcharts/ReactHighstock';
import extendExporting from 'highcharts-exporting';
extendExporting(ReactHighstock.Highcharts);

import {fetchTimeline, getPerfs} from '../actions/phaseActions.js';
import {fetchInfo, setAppState} from '../actions/phaseActions.js';

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
            step: true,
        },
    },
    rangeSelector: {
        allButtonsEnabled: true,
        selected: 5,
        buttons: [{
            type: 'millisecond',
            count: 20,
            text: 'ms',
        }, {
            type: 'second',
            count: 5,
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
        zoomType: 'x',
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
        appInfo: store.phase.appInfo,
        appState: store.phase.appState,
    };
})
export default class PhaseTimeline extends React.Component {
    constructor() {
        super();

        this.config = {};
        this.state = {
            similarityThreshold: 0,
            timePerspective: 'host',
        };

        // This binding is necessary to make `this` work in the callback
        this.handleSliderChange = this.handleSliderChange.bind(this);
        this.handlePerspectiveChange = this.handlePerspectiveChange.bind(this);
        this.handleSelectProcess = this.handleSelectProcess.bind(this);
    }

    // When the DOM is ready, create the chart.
    componentWillMount() {
        this.config = JSON.parse(JSON.stringify(defaultOptions));

        // Assign inital value of data series
        // TODO This is not that good
        for (let i = 0; i < 16; i++) {
            this.config.series.push(this.createSeries());
        }

        // Set initial value if it's not assigned
        let similarityThreshold = this.props.similarityThreshold;
        this.setState({similarityThreshold: similarityThreshold});

        this.props.dispatch(fetchInfo('processes'));
        this.props.dispatch(fetchTimeline(similarityThreshold, this.state.timePerspective));
    }

    createSeries() {
        // Push a new series of our default config with deep copy
        const newSeries = JSON.parse(JSON.stringify(defaultSeries));
        // Assign data to the first series
        newSeries.data = [];
        // Assign mouse event to the first series
        newSeries.point.events.select = this.selectEvent.bind(this);

        return newSeries;
    }

    selectEvent(event) {
        const selectedItem = event.target['y'];
        const selectedProcessID = parseInt(event.target.series.name) || null;

        if (selectedItem && selectedProcessID) {
            this.props.dispatch(getPerfs(selectedItem, this.state.similarityThreshold, selectedProcessID));
            return true;
        }
        return false;
    }

    handleSliderChange(value) {
        const {appState} = this.props;
        this.setState({similarityThreshold: value});
        this.props.dispatch(fetchTimeline(value, this.state.timePerspective, appState.selectedProcess));
    }

    handlePerspectiveChange(e) {
        const {appState} = this.props;
        let perspective = 'host';

        if (this.state.timePerspective == 'host') {
            perspective = 'guest';
        } else {
            perspective = 'host';
        }
        this.setState({timePerspective: perspective});
        this.props.dispatch(fetchTimeline(this.state.similarityThreshold, perspective, appState.selectedProcess));
    }

    handleSelectProcess(e) {
        let selectedProcess = e.target.value;
        this.props.dispatch(setAppState('selectedProcess', selectedProcess));
        this.props.dispatch(fetchTimeline(this.state.similarityThreshold, this.state.timePerspective, selectedProcess));
    }

    render() {
        console.log('PhaseTimeline');
        const {timeline} = this.props;
        const {appInfo} = this.props;
        const {appState} = this.props;

        if (timeline.error) {
            let chart = this.chart.getChart();
            chart.showLoading('Timeline Result Not Found');
        } else if (timeline.fetching) {
            let chart = this.chart.getChart();
            chart.showLoading('Loading data from server...');
        } else if (timeline.fetched) {
            let chart = this.chart.getChart();
            // TODO This ugly solution is bad and low performance
            if (timeline.data[0].length == 2) {
                // If the size of first element is 2 means it's a 1-D timeline
                chart.series[0].setData(timeline.data);

                if (appState.selectedProcess == '') {
                    chart.series[0].name = appInfo.processes[0];
                } else {
                    chart.series[0].name = appState.selectedProcess;
                }
                for (var i = 1; i < chart.series.length; i++) {
                    chart.series[i].setData([]);
                }
            } else {
                // The data contains multiple series
                for (var i = 0; i < chart.series.length; i++) {
                    chart.series[i].setData([]);
                }
                for (var i = 0; i < timeline.data.length; i++) {
                    chart.series[i].setData(timeline.data[i]);
                    chart.series[i].name = appInfo.processes[i];
                }
            }
            chart.hideLoading();
        }

        return (
            <div>
                <div className='col-md-12'>
                    <div className='col-md-3'>
                        <SimilaritySlider
                            onChange={this.handleSliderChange}
                            value={this.state.similarityThreshold} />
                    </div>
                    <div className='col-md-1 tg-list' style={{marginTop: '25px'}}>
                        <input className="tgl tgl-skewed" id="cb3" type="checkbox" onChange={this.handlePerspectiveChange}/>
                        <label className="tgl-btn center" data-tg-off="host" data-tg-on="guest" htmlFor="cb3"/ >
                    </div>
                    <div className='col-md-2'>
                        <p>Process: </p>
                        <select className="select_box" onChange={this.handleSelectProcess} value={appState.selectedProcess}>
                            {appInfo.processes.map((pid, i) =>
                                <option key={pid} value={pid}>{pid}</option>
                            )}
                            <option key='all' value='all'>all</option>
                        </select>
                    </div>
                </div>
                <div className='col-md-12'>
                    <ReactHighstock
                        config={this.config}
                        isPureConfig={true}
                        ref={(ref) => this.chart = ref} />
                </div>
            </div>
        );
    }
}
