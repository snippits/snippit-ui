import React from "react";
import { connect } from "react-redux"

import Highlight from 'react-highlight';

import { fetchCode } from "../actions/phaseActions.js"

@connect((store) => {
  return {
    code: store.phase.code,
  };
})
export default class CodeResult extends React.Component {
    constructor() {
        super()

        this.last_selected_phase_id = -1;
        this.state = {code: ""};
    }

    loadPhaseCode(phase_id, cb) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                cb(this.responseText);
            }
            else {
                cb("");
            }
        };
        var link = "output/phase-code-" + phase_id;
        xhttp.open("GET", link + "?_=" + new Date().getTime(), true);
        xhttp.send();
    }

    loadCode(phase_id) {
        this.loadPhaseCode(phase_id, function(data) {
            this.setState({code: data});
        }.bind(this));
    }

    componentDidMount() {
    }

    render() {
        if (this.last_selected_phase_id != this.props.selected_phase_id) {
            // Only reload when it's not the same as last id
            // this.loadCode(this.props.selected_phase_id);
            this.props.dispatch(fetchCode(this.props.selected_phase_id));
        }
        this.last_selected_phase_id = this.props.selected_phase_id;

        return (
            <div class="col-md-6">
                <h1 class="pure-u-1-1">Code</h1>
                <Highlight className='C++'>
                    {JSON.stringify(this.props.code.data, null, 4)}
                </Highlight>
            </div>
        );
    }
}
