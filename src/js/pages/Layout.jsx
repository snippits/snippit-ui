import React from 'react';
import { Link, Route } from 'react-router-dom';

import Phase from './Phase';

export default class Layout extends React.Component {
  render() {
    const {location} = this.props;
    const {match} = this.props;

    const timelineStyle = {
      height: '500px',
      minWidth: '310px',
    };
    const treemapStyle = {
      height: '300px',
      minWidth: '310px',
    };

    // Set to empty string to make the route work at index
    if (match.url === '/') match.url = '';

    console.log('layout');
    return (
        <div class='row'>
          <div class='col-12'>
            <h1>Snippit UI</h1>
          </div>
          <div class='col-12'>
            <Route path={`${match.url}/:page?/:phaseID?`} component={Phase} />
          </div>
        </div>
    );
  }
}
