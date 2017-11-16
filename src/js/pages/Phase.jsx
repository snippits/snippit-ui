import React from 'react';

import PhaseTimeline from '../components/PhaseTimeline';
import PhaseTreeMap from '../components/PhaseTreeMap';
import CodeResult from '../components/CodeResult';
import ProfilingResult from '../components/ProfilingResult';

export default class Phase extends React.Component {
    constructor() {
        super();
        this.state = {
        };
    }

    componentWillMount() {
    }

    componentDidMount() {
    }

    render() {
        console.log('Phase');

        // setTimeout(function(){this.forceUpdate();}.bind(this), 2000);
        return (
            <div>
                <PhaseTimeline similarityThreshold={90}/>
                <CodeResult />
                <ProfilingResult />
                <PhaseTreeMap />
            </div>
        );
    }
}
