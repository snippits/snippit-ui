import React from 'react';
import {connect} from 'react-redux';

import Highlight from 'react-highlight';

@connect((store) => {
    return {
        code: store.phase.code,
    };
})
export default class CodeResult extends React.Component {
    constructor() {
        super();
    }

    componentDidMount() {
    }

    render() {
        const {code} = this.props;
        let output = code.data;

        console.log('CodeResult');

        if (code.error) {
            console.log('Cannot fetch the codes');
            output = [];
        }

        // This is used to force clean all browser implicit state and rebuild component
        const codekey = 'phase-' + code.phaseID + '-time-' + new Date().getTime();
        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Code</h1>
                <HighlightedCode key={codekey} value={output}/>
            </div>
        );
    }
}

class HighlightedCode extends React.Component {
    generateTable(values) {
        if (typeof values === 'string') {
            return values;
        } else {
            return values.map((code, i) =>
                <tr key={i} className='no-border'>
                    <td className='col-md-1 walk-count'>{code.walk}</td>
                    <td className='line-num'>{i} </td>
                    <td className='code'>{code.line}</td>
                </tr>
            );
        }
    }

    render() {
        const output = this.generateTable(this.props.value);

        return (
            <Highlight className='C++'>
                <table className='table table-hover table-condensed table-borderless'>
                    <tbody>
                        {output}
                    </tbody>
                </table>
            </Highlight>
        );
    }
}
