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
            showOnlyWalked: false,
            content: [],
        };

        this.handleSelectFile = this.handleSelectFile.bind(this);
        this.toggleContent = this.toggleContent.bind(this);
    }

    componentDidMount() {
    }

    handleSelectFile(e) {
        const {dispatch} = this.props;
        const selectedFile = e.target.value;

        this.setState({selectedFile: selectedFile});
        dispatch(fetchFile(selectedFile, (content) => {
            this.setState({content: content});
        }));
    }

    toggleContent(e) {
        this.setState({showOnlyWalked: !this.state.showOnlyWalked});
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
            const lookupMapping = codes
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

            codes = this.state.content
                .map((line, idx) => {
                    if (lookupTable[idx]) {
                        return {lineNum: idx, line: line, walk: lookupTable[idx].walk};
                    }
                    if (!this.state.showOnlyWalked) {
                        return {lineNum: idx, line: line, walk: undefined};
                    }
                })
                .filter((element) => {
                    return element !== undefined;
                });
        }

        // This is used to force clean all browser implicit state and rebuild component
        const codekey = 'phase-' + code.phaseID + '-time-' + new Date().getTime();
        return (
            <div className='col-md-6'>
                <h1 className='pure-u-1-1'>Code</h1>
                <div>
                    <input type='button' className='col-md-1 btn btn-primary'
                        onClick={this.toggleContent}>
                    </input>
                    <select className='select_box col-md-11'
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
                    <td className='line-num'>{code.lineNum || i}</td>
                    <td className='code'>{code.line + '\n'}</td>
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
