import React from "react";
import { connect } from "react-redux"

import PhaseTimeline from "../components/PhaseTimeline";
import PhaseTreeMap from "../components/PhaseTreeMap";
import CodeResult from "../components/CodeResult";
import ProfilingResult from "../components/ProfilingResult";

import * as phaseActions from "../actions/phaseActions.js"

@connect((store) => {
  return {
    phase: store.phase,
  };
})
export default class Phase extends React.Component {
    constructor() {
        super()
        this.state = {
            selected_phase_id: -1,
        };
    }

    componentWillMount() {
        //this.props.dispatch(phaseActions.fetchTimeline(90));
        //this.props.dispatch(phaseActions.fetchProf(9));
    }

    componentDidMount() {
    }

    select_event(event) {
        var selectedItem = event.target["y"];
        console.log(selectedItem)
        if (selectedItem) {
            this.setState({selected_phase_id: selectedItem});
            return true;
        }
        return false;
    }

    render() {
        console.log("phase");
        // setTimeout(function(){this.forceUpdate();}.bind(this), 2000);
        return (
            <div>
                <PhaseTimeline select_event={this.select_event.bind(this)}/>
                <PhaseTreeMap selected_phase_id={this.state.selected_phase_id}/>
                <CodeResult selected_phase_id={this.state.selected_phase_id}/>
                <ProfilingResult selected_phase_id={this.state.selected_phase_id}/>
            </div>
        );

    }
}
