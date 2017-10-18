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
        const output = [];
        // This is used to force clean all browser implicit state and rebuild component
        const codekey = 'phase-' + code.phaseID + '-highlighted-code-' + new Date().getTime();

        console.log('CodeResult');

        if (code.error) {
            console.log('Cannot fetch the codes');
        } else if (code.fetched) {
            for (let i = 0; i < code.data.length; i++) {
                output.push({
                    code: code.data[i].line,
                });
            }
        }

        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Code</h1>
                <HighlightedCode key={codekey} codes={output}/>
            </div>
        );
    }
}

class HighlightedCode extends React.Component {
    render() {
        return (
            <Highlight className='C++'>
                <table>
                    <tbody>
                        {this.props.codes.map(function(object, i) {
                            return <tr key={i}>
                                <td>{i} </td>
                                <td>{object.code}</td>
                            </tr>;
                        })}
                    </tbody>
                </table>
            </Highlight>
        );
    }
}
