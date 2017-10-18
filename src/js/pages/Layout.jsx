import React from 'react';
import {Route} from 'react-router-dom';

import Phase from './Phase';

export default class Layout extends React.Component {
    render() {
        const {match} = this.props;

        // Set to empty string to make the route work at index
        if (match.url === '/') match.url = '';

        console.log('layout');
        return (
            <div className='row'>
                <div className='col-12'>
                    <h1>Snippit UI</h1>
                </div>
                <div className='col-12'>
                    <Route path={`${match.url}/:page?/:phaseID?`} component={Phase} />
                </div>
            </div>
        );
    }
}
