import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { syncHistoryWithStore } from 'react-router-redux';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import configureStore from './store/configureStore';
import blue from '@material-ui/core/colors/blue';
import App from './app';
import './style.scss';

console.log("App:",App);

//require('expose?$!expose?jQuery!jquery');
//require('bootstrap-webpack');

//injectTapEventPlugin();
const store = configureStore();
//const history = syncHistoryWithStore(browserHistory, store);

const theme = createMuiTheme({
  palette: {
    primary: blue,
  },
});

ReactDOM.render((
	<MuiThemeProvider theme={theme}>
    	<BrowserRouter>
        	<Provider store={store}>
	    		<App/>
	    	</Provider>
    	</BrowserRouter>
   	</MuiThemeProvider>),
    document.getElementById('root')
);
