import React from 'react';
import {connect} from 'react-redux';

import Highlight from 'react-highlight';

import {fetchFile} from '../actions/phaseActions.js';

@connect((store) => {
    return {
        files: store.phase.files,
        code: store.phase.code,
    };
})
export default class CodeResult extends React.Component {
    constructor() {
        super();
        this.state = {
            selectedFile: '',
            content: [],
            codes: [],
        };

        this.handleSelectFile = this.handleSelectFile.bind(this);
    }

    componentDidMount() {
    }

    handleSelectFile(e) {
        const {dispatch} = this.props;
        const selectedFile = e.target.value;

        this.setState({selectedFile: selectedFile});
        this.props.dispatch(fetchFile(selectedFile, (content) => {
            const lookupMapping = this.props.code.data
                .map((lineInfo) => {
                    if (lineInfo.line.startsWith(this.state.selectedFile)) {
                        const tmp = lineInfo.line.split(':');
                        const lineNum = tmp[tmp.length - 1];
                        return {line: lineNum, walk: lineInfo.walk};
                    }
                })
                .filter((element) => {
                    return element !== undefined;
                });
            let lookupTable = [];
            for (let i = 0; i < lookupMapping.length; i++) {
                const {line, walk} = lookupMapping[i];
                lookupTable[line] = {walk: walk};
            }

            const codes = content.map((line, idx) => {
                if (lookupTable[idx]) return {line: line, walk: lookupTable[idx].walk};
                return {line: line, walk: null};
            });

            this.setState({content: content, codes: codes});
        }));
    }

    render() {
        const {code} = this.props;
        const {files} = this.props;
        let codes = code.data;

        console.log('CodeResult');

        if (code.error) {
            console.log('Cannot fetch the codes');
            codes = [];
        }
        if (this.state.selectedFile !== '') {
            codes = this.state.codes;
        }

        // This is used to force clean all browser implicit state and rebuild component
        const codekey = 'phase-' + code.phaseID + '-time-' + new Date().getTime();
        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Code</h1>
                <div>
                    <select className='select_box col-md-12'
                        onChange={this.handleSelectFile} value={this.state.selectedFile}>

                        <option key='no-select' value=''></option>
                        {files.data.map((filePath) =>
                            <option key={filePath} value={filePath}>{filePath}</option>
                        )}
                    </select>
                </div>
                <HighlightedCode key={codekey} value={codes}/>
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
