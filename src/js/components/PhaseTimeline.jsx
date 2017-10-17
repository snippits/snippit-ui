import React from 'react';
import { connect } from 'react-redux';

import Highcharts from 'highcharts';
import ReactHighstock from 'react-highcharts/ReactHighstock';
import SimilaritySlider from '../components/SimilaritySlider';

import { fetchTimeline, setSimilarityThreshold, setSelectedPhase } from '../actions/phaseActions.js';

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
    };
  }

  // When the DOM is ready, create the chart.
  componentWillMount() {
    this.config = JSON.parse(JSON.stringify(default_options));

    // Push a new series of our default config with deep copy
    var new_series = JSON.parse(JSON.stringify(default_series));
    // Change marker line color (not series line color)
    new_series.marker.lineColor = '#FFFFFF';
    // Assign data to the first series
    new_series.data = [];
    // Assign mouse event to the first series
    new_series.point.events.select = this.select_event.bind(this);
    // Assign inital value of data series
    this.config.series.push(new_series);

    // Set initial value if it's not assigned
    var similarity_threshold = this.props.similarity_threshold;
    if (similarity_threshold === undefined) similarity_threshold = 100;
    this.props.dispatch(setSimilarityThreshold(similarity_threshold));
    this.props.dispatch(fetchTimeline(similarity_threshold));
  }

  select_event(event) {
    var selectedItem = event.target['y'];
    // console.log(selectedItem)
    if (selectedItem !== undefined) {
      this.props.dispatch(setSelectedPhase(selectedItem));
      return true;
    }
    return false;
  }

  handle_slider_change(value) {
    this.props.dispatch(setSimilarityThreshold(value));
    this.props.dispatch(fetchTimeline(value));
  }

  render() {
    console.log('PhaseTimeline');
    const {timeline} = this.props;

    if (timeline.error) {
      let chart = this.refs.chart.getChart();
      chart.showLoading('Timeline Result Not Found');
    } else if (timeline.fetching) {
      let chart = this.refs.chart.getChart();
      chart.showLoading('Loading data from server...');
    } else if (timeline.fetched) {
      let chart = this.refs.chart.getChart();
      chart.series[0].setData(timeline.data);
      chart.hideLoading();
    }

    return (
        <div class='col-md-12'>
          <SimilaritySlider set_change={this.handle_slider_change.bind(this)}
            similarity_threshold={timeline.similarity_threshold} />
          <ReactHighstock config={this.config} isPureConfig={true} ref='chart'></ReactHighstock>
        </div>
    );
  }
}
