import React from 'react';
import ReactDOM from 'react-dom';
import {createStore, applyMiddleware} from 'redux';
import thunk from 'redux-thunk';
import {Provider} from 'react-redux';
import 'bootstrap/dist/css/bootstrap.min.css';
import Web3Provider, {Connectors} from 'web3-react'


import SessionDetail from './components/sessionDetail/index';
import SessionCreate from './components/sessionCreate/index';
import * as serviceWorker from './serviceWorker';
import rootReducer from './reducers';
import gitCoinApi from "./api";
import Web3 from "web3";
import {Web3Consumer} from "web3-react";
import {BrowserRouter as Router, Route, Link} from "react-router-dom";


// TODO get url from process.env?
let api = gitCoinApi();


// set up web3-react
const {InjectedConnector, NetworkOnlyConnector} = Connectors
// const MetaMask = new InjectedConnector({supportedNetworks: [1, 4]})
const MetaMask = new InjectedConnector();
const Infura = new NetworkOnlyConnector({
  providerURL: 'https://mainnet.infura.io/v3/...'
})

const connectors = {MetaMask, Infura};


const store = createStore(rootReducer,
  applyMiddleware(
    thunk.withExtraArgument(api)
  ));


ReactDOM.render(<Provider store={store}>
    <Web3Provider
      connectors={connectors}
      libraryName={"web3.js"}
      web3Api={Web3}
    >
      <Router>
        <div>
          <Route path="/experts/new/" exact component={SessionCreate}/>
          <Route path="/experts/sessions/:id"
                 render={(props) => <Web3Consumer>
                   {context => <SessionDetail
                     {...props}
                     web3Context={context}
                   />}
                 </Web3Consumer>
                 }
          />
        </div>
      </Router>


    </Web3Provider>
  </Provider>,
  document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
