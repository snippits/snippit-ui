import React from "react";

export default class SimilaritySlider extends React.Component {
    constructor() {
        super();
    }

    handleChange(e) {
        this.props.set_change(e.target.value);
    }

    render() {
        console.log("SimilaritySlider");
        return (
            <div class="col-md-12">
                <div class="col-md-3">
                    <p>Phase Similarity Filter:</p>
                    <input type="range" min="0" max="100" step="10"
                        value={this.props.similarity_threshold} onChange={this.handleChange.bind(this)}>
                    </input>
                </div>
            </div>
        );
    }
}
