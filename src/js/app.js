import React from "react";
import ReactDOM from "react-dom";
import { Router, Route, IndexRoute, hashHistory } from "react-router";

import { Provider } from "react-redux"
import store from "./store"

import Phase from "./pages/Phase";
import Layout from "./pages/Layout";

const app = document.getElementById('app');

ReactDOM.render(
<Provider store={store}>
  <Router history={hashHistory}>
    <Route path="/" component={Layout}>
      <IndexRoute component={Phase}></IndexRoute>
    </Route>
  </Router>
</Provider>,
app);
