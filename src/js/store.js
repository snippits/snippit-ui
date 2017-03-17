import { applyMiddleware, createStore } from "redux"

import logger from "redux-logger"
import thunk from "redux-thunk"
import promise from "redux-promise-middleware"
import multi from 'redux-multi'

import reducer from "./reducers"

const middleware = applyMiddleware(multi, promise(), thunk, logger())

export default createStore(reducer, middleware)
