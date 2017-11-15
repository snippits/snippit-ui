import React from 'react';
import {connect} from 'react-redux';

import SimilaritySlider from '../components/SimilaritySlider';
import ReactHighstock from 'react-highcharts/ReactHighstock';
import extendExporting from 'highcharts-exporting';
extendExporting(ReactHighstock.Highcharts);

// boost does not work properly, donnot enable it yet
// import extendBoost from 'highcharts-boost';
// extendBoost(ReactHighstock.Highcharts);

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

    boost: {
        useGPUTranslations: false,
    },

    tooltip: {
        split: true,
        pointFormat: ' <span style="color:{series.color}">● </span><b>{series.name} :</b> Phase <b>{point.y}</b> <br/>',
        changeDecimals: 0,
        valueDecimals: 0,
    },

    scrollbar: {
        liveRedraw: false,
    },

    series: [],
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
        this.timelineID = 0;

        // This binding is necessary to make `this` work in the callback
        this.handleSliderChange = this.handleSliderChange.bind(this);
        this.handlePerspectiveChange = this.handlePerspectiveChange.bind(this);
        this.handleSelectProcess = this.handleSelectProcess.bind(this);
    }

    // When the DOM is ready, create the chart.
    componentWillMount() {
        this.config = JSON.parse(JSON.stringify(defaultOptions));

        // Set initial value if it's not assigned
        let similarityThreshold = this.props.similarityThreshold;
        this.setState({similarityThreshold: similarityThreshold});

        // Fetch info and then setup default process with fetching its timeline
        this.props.dispatch(fetchInfo('processes', (info) => {
            const processID = info['processes'][0]; // Default: First parent process
            this.props.dispatch([
                setAppState('selectedProcess', processID),
                fetchTimeline(similarityThreshold, this.state.timePerspective, processID),
            ]);
        }));
    }

    createSeries(name, data) {
        const newSeries = {
            name: name,
            marker: {
                enabled: null, // auto
                radius: 3,
                lineWidth: 1,
            },
            linecap: 'round',
            allowPointSelect: true,
            showCheckbox: false,
            selected: true,
            data: data,
            point: {events: {
                // Assign mouse event to the first series
                select: this.selectEvent.bind(this),
            }},
            dataGrouping: {
                enabled: false,
            },
            boostThreshold: 1000,
        };

        return newSeries;
    }

    updateSeries(chart, names, series) {
        // Minus 1 for the navigator
        if (chart.series.length - 1 != series.length) {
            while (chart.series.length > 0) {
                // Donot redraw while removing series
                chart.series[0].remove(false);
            }
            for (let i = 0; i < series.length; i++) {
                // Donot redraw while adding new series
                chart.addSeries(this.createSeries(names[i], series[i]), false);
            }
        } else {
            for (let i = 0; i < series.length; i++) {
                chart.series[i].setData(series[i], false);
                chart.series[i].name = names[i];
            }
        }
        // redraw after some delay for DOM updates
        setTimeout(() => {
            chart.redraw();
        }, 20);
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
        const {dispatch, appState} = this.props;

        this.setState({similarityThreshold: value});
        this.timelineID++;
        dispatch(fetchTimeline(value, this.state.timePerspective, appState.selectedProcess, this.timelineID));
    }

    handlePerspectiveChange(e) {
        const {dispatch, appState} = this.props;
        // Toggle the perspective
        const perspective = (this.state.timePerspective === 'host') ? 'guest' : 'host';

        this.setState({timePerspective: perspective});
        dispatch(fetchTimeline(this.state.similarityThreshold, perspective, appState.selectedProcess));
    }

    handleSelectProcess(e) {
        const {dispatch} = this.props;
        const selectedProcess = e.target.value;

        dispatch(setAppState('selectedProcess', selectedProcess));
        dispatch(fetchTimeline(this.state.similarityThreshold, this.state.timePerspective, selectedProcess));
    }

    render() {
        console.log('PhaseTimeline');
        const {timeline} = this.props;
        const {appInfo} = this.props;
        const {appState} = this.props;

        if (timeline.error) {
            const chart = this.chart.getChart();
            chart.showLoading('Timeline Result Not Found');
        } else if (timeline.fetching) {
            const chart = this.chart.getChart();
            chart.showLoading('Loading data from server...');
        } else if (timeline.fetched) {
            const chart = this.chart.getChart();
            const series = (timeline.data[0].length == 2) ? [timeline.data] : timeline.data;
            const names = (appState.selectedProcess === 'all') ? appInfo.processes : [appState.selectedProcess];

            // window.timelineChart = chart;
            // Only draw the latest one, skipping the outdated responses
            if (timeline.id == this.timelineID) {
                this.updateSeries(chart, names, series);
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
                        <input type="checkbox" className="tgl tgl-skewed" id="cb3"
                            onChange={this.handlePerspectiveChange}/>
                        <label className="tgl-btn center" data-tg-off="host" data-tg-on="guest" htmlFor="cb3"/ >
                    </div>
                    <div className='col-md-2'>
                        <p>Process: </p>
                        <select className="select_box"
                            onChange={this.handleSelectProcess} value={appState.selectedProcess}>

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
