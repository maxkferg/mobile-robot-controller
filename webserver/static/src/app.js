/* eslint new-cap: 0 */

import React from 'react';
import { Switch, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Home from './components/Home';
import Accelerometer from './components/Accelerometer';
import LoginView from './components/LoginView';
import RegisterView from './components/RegisterView';
import ProtectedView from './components/ProtectedView';
import Analytics from './components/Analytics';
import NotFound from './components/NotFound';

import { DetermineAuth } from './components/DetermineAuth';
import { requireAuthentication } from './components/AuthenticatedComponent';
import { requireNoAuthentication } from './components/notAuthenticatedComponent';


class App extends React.Component {
    render() {
        return (
			<div className="App">
				<Header />
				<main>
				    <Switch>
				        <Route path="/" exact component={requireNoAuthentication(Home)} />
				        <Route path="/accelerometer" exact component={requireNoAuthentication(Accelerometer)} />
				        <Route path="login" component={requireNoAuthentication(LoginView)} />
				        <Route path="register" component={requireNoAuthentication(RegisterView)} />
				        <Route path="analytics" component={requireAuthentication(Analytics)} />
				        <Route path="*" component={DetermineAuth(NotFound)} />
				    </Switch>
				</main>
			    <Footer />
			</div>
        );
    }
}

export default App;
