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
    }

    componentDidMount() {
    }

    render() {
        const { code } = this.props;
        console.log("CodeResult");

        var output = "";
        if (code.error) {
            output = [];
        } else if (code.fetched) {
            if (typeof code.data === "string") {
                output = code.data
            } else {
                output = JSON.stringify(code.data, null, 4)
            }
        }

        return (
            <div class="col-md-6">
                <h1 class="pure-u-1-1">Code</h1>
                <Highlight className='C++'>
                    {output}
                </Highlight>
            </div>
        );
    }
}
