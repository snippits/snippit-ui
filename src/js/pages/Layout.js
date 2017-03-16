import React from "react";
import { Link } from "react-router";

import Footer from "../components/layout/Footer";

export default class Layout extends React.Component {
  render() {
    const { location } = this.props;
    const containerStyle = {
      marginTop: "30px"
    };
    const timelineStyle = {
      height: "500px",
      minWidth: "310px",
    };
    const treemapStyle = {
      height: "300px",
      minWidth: "310px",
    };

    console.log("layout");
    return (
        <div class="container-fluid" style={containerStyle}>
          <div class="row">
            <div class="col-12">
              <h1>Snippit UI</h1>
            </div>
            <div class="col-12">
              {this.props.children}
            </div>
          </div>
          <Footer/>
        </div>
    );
  }
}
