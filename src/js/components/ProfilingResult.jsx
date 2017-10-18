import React from 'react';
import {connect} from 'react-redux';

@connect((store) => {
    return {
        prof: store.phase.prof,
    };
})
export default class ProfilingResult extends React.Component {
    constructor() {
        super();
    }

    componentDidMount() {
    }

    render() {
        const {prof} = this.props;
        console.log('ProfilingResult');

        let output = '';
        if (prof.error) {
            output = 'Profiling Result Not Found';
        } else if (prof.fetched) {
            output = prof.data.text;
        }

        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Profiling Result</h1>
                <pre>
                    {output}
                </pre>
            </div>
        );
    }
}
