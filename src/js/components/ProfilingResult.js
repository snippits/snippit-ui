import React from "react";
import { connect } from "react-redux"

import { fetchProf } from "../actions/phaseActions.js"

@connect((store) => {
  return {
    prof: store.phase.prof,
  };
})
export default class ProfilingResult extends React.Component {
    constructor() {
        super()

        this.last_selected_phase_id = -1;
        this.state = {plain_result: ""};
    }

    loadPhaseProf(phase_id, cb) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                cb(this.responseText);
            }
            else {
                cb("");
            }
        };
        var link = "output/phase-prof-" + phase_id;
        xhttp.open("GET", link + "?_=" + new Date().getTime(), true);
        xhttp.send();
    }

    loadProf(phase_id) {
        this.loadPhaseProf(phase_id, function(data) {
            this.setState({plain_result: data});
        }.bind(this));
    }

    componentDidMount() {
    }

    render() {
        if (this.last_selected_phase_id != this.props.selected_phase_id) {
            // Only reload when it's not the same as last id
            // this.loadProf(this.props.selected_phase_id);
            this.props.dispatch(fetchProf(this.props.selected_phase_id));
        }
        this.last_selected_phase_id = this.props.selected_phase_id;

        return (
            <div class="col-md-6">
                <h1 class="pure-u-1-1">Profiling Result</h1>
                <pre>
                {this.props.prof.data}
                </pre>
            </div>
        );
    }
}
