import React, { Component } from 'react';
import gql from "graphql-tag";
import { graphql } from "react-apollo";
import { HttpLink } from 'apollo-link-http';
import { ApolloProvider } from 'react-apollo';
import { withStyles } from '@material-ui/core/styles';
import ApolloClient from "apollo-boost";
import Typography from '@material-ui/core/Typography';
import Wheels from '../Home/wheels';
import Accelerometer from './accelerometer.js';


const styles = theme => ({
  root: {
    flexGrow: 1,
  },
  paper: {
    padding: theme.spacing.unit * 2,
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
  section:{
    paddingBottom: "100px",
  }
});



class Home extends Component {
  constructor(props) {
    super(props);
    this.state = {
      leftWheel:  null,
      rightWheel: null
    };
    this.onMove = this.onMove.bind(this);
  }

  createClient() {
    // Initialize Apollo Client with URL to our server
    return new ApolloClient({
      link: new HttpLink({
        uri: 'http://localhost:5000/graph.ql'
      }),
      connectToDevTools: true,
    });
  }

  onMove(event){
    const MAX = 30;
    const MIN = -30;
    const SCALE = 50/MAX;
    let forward = event.beta; //[-180, 180]
    let turn = event.gamma;
    turn = SCALE * Math.max(Math.min(MAX, turn), MIN);
    forward = SCALE * Math.max(Math.min(MAX, forward), MIN);
    let leftWheel = forward + turn;
    let rightWheel = forward - turn;
    this.setState({leftWheel: leftWheel, rightWheel: rightWheel});
  }

  render() {
    const { classes } = this.props;
    return (
      // Feed the client instance into your React component tree
      <ApolloProvider client={this.createClient()}>
        <section className={classes.section}>
            <Typography variant="display1" align="center">Accelerometer</Typography>
            <Wheels leftWheel={this.state.leftWheel} rightWheel={this.state.rightWheel} disabled />
        </section>
        <section className={classes.section}>
            <Accelerometer onMove={this.onMove}/>
        </section>
      </ApolloProvider>
    );
  }
}

export default withStyles(styles)(Home);