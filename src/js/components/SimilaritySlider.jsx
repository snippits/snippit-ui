import React from 'react';

export default class SimilaritySlider extends React.Component {
    constructor() {
        super();
        // This binding is necessary to make `this` work in the callback
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(e) {
        this.props.onChange(e.target.value);
    }

    render() {
        console.log('SimilaritySlider');
        return (
            <div className='col-md-12'>
                <div className='col-md-3'>
                    <p>Phase Similarity Filter:</p>
                    <input type='range' min='0' max='100' step='10'
                        value={this.props.value} onChange={this.handleChange}>
                    </input>
                </div>
            </div>
        );
    }
}
