import React from 'react';
import ReactDOM from 'react-dom';
import {Route} from 'react-router';
import {HashRouter} from 'react-router-dom';

import {Provider} from 'react-redux';
import store from './store';

import Layout from './pages/Layout';
import Footer from './components/layout/Footer';

const app = document.getElementById('app');

const containerStyle = {
    marginTop: '30px',
};

ReactDOM.render(
    <Provider store={store}>
        <HashRouter>
            <div className='container-fluid' style={containerStyle}>
                <Route path='/' component={Layout} />
                <Footer/>
            </div>
        </HashRouter>
    </Provider>,
    app);
