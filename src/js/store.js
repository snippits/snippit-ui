import {applyMiddleware, createStore} from 'redux';
import {createLogger} from 'redux-logger';

import thunk from 'redux-thunk';
import promiseMiddleware from 'redux-promise-middleware';
import multi from 'redux-multi';

import reducer from './reducers';

const middlewares = [multi, promiseMiddleware(), thunk];

const logger = createLogger({
    collapsed: (getState, action, logEntry) => !logEntry.error,
    duration: true,
});

middlewares.push(logger);

export default createStore(reducer, applyMiddleware(...middlewares));
