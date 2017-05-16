import React, { Component } from 'react';
import RaisedButton from 'material-ui/RaisedButton';
import { gql, graphql } from 'react-apollo';
import { ApolloClient, ApolloProvider, createNetworkInterface } from 'react-apollo';

const style = {
  margin: 12,
};


const CarQuery = gql`
query Car {
  car {
    rotation
    throttle
  }
}`


const CarMutation = gql`
mutation Car($left: Float, $right: Float, $accelerate: Float, $decelerate: Float, $reset: Boolean) {
  controlCar(left: $left, right: $right, accelerate: $accelerate, decelerate: $decelerate, reset: $reset) {
    car {
      rotation
      throttle
    }
  }
}`



@graphql(CarQuery)
@graphql(CarMutation)
export class Dashboard extends Component {

  reset = () => {
    this.props.mutate({
      update: this.update,
      variables: { reset: true }
    });
  }

  accelerate = () => {
    this.props.mutate({
      update: this.update,
      variables: { accelerate: 0.1}
    });
  }

  decelerate = () => {
    this.props.mutate({
      update: this.update,
      variables: {decelerate: 0.1}
    });
  }

  turnLeft = () => {
    this.props.mutate({
      update: this.update,
      variables: {left: 0.1}
    });
  }

  turnRight = () => {
    this.props.mutate({
      update: this.update,
      variables: {right: 0.1}
    });
  }

  update = (store, mutation) => {
    const data = store.readQuery({ query: CarQuery });
    data.car = mutation.data.controlCar.car
    store.writeQuery({ query: CarQuery, data });
  }

  render() {
    let rotation = 0;
    let throttle = 0;

    if (this.props.data.car){
        rotation = parseFloat(this.props.data.car.rotation).toFixed(2);
        throttle = parseFloat(this.props.data.car.throttle).toFixed(2);
    }

    return (
        // Feed the client instance into your React component tree
        <div>
            <h1>Steering: ({ rotation })</h1>
            <div>
                <RaisedButton label="Left" primary={true} style={style} onClick={this.turnLeft} />
                <RaisedButton label="Right" secondary={true} style={style} onClick={this.turnRight} />
            </div>
            <h1>Throttle: ({ throttle })</h1>
            <div>
                <RaisedButton label="Accelerate" primary={true} style={style} onClick={this.accelerate} />
                <RaisedButton label="Decelerate" secondary={true} style={style} onClick={this.decelerate} />
            </div>
            <h1>Reset</h1>
            <div>
                <RaisedButton label="Reset" primary={true} style={style} onClick={this.reset} />
            </div>
        </div>  
    );
  }
}






export class Home extends Component {
  createClient() {
    // Initialize Apollo Client with URL to our server
    return new ApolloClient({
      networkInterface: createNetworkInterface({
        uri: '/graphql',
      }),
    });
  }

  render() {
    return (
      // Feed the client instance into your React component tree
      <ApolloProvider client={this.createClient()}>
        <section>
            <div className="container text-center">
                <Dashboard />
            </div>
        </section>
      </ApolloProvider>
    );
  }
}