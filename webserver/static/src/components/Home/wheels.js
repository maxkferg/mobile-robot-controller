import React, { Component } from 'react';
import gql from "graphql-tag";
import { graphql } from "react-apollo";
import Slider from '@material-ui/lab/Slider';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import { HttpLink } from 'apollo-link-http';
import { ApolloProvider } from 'react-apollo';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';


const styles = {
  root: {
    display: 'flex',
    flexDirection: 'column',
    height: '50%',
  },
  slider: {
    width: "2px",
    marginLeft: "auto",
    marginRight: "auto",
  },
  button: {
    marginLeft: "auto",
    marginRight: "auto",
  },
};


const CarQuery = gql`
query Car {
  car {
    leftWheel
    rightWheel
  }
}`



const CarMutation = gql`
mutation Car($leftWheel: Float, $rightWheel: Float) {
  controlCar(leftWheel: $leftWheel, rightWheel: $rightWheel) {
    car {
      leftWheel
      rightWheel
    }
  }
}`



@graphql(CarQuery)
@graphql(CarMutation)
class Wheels extends Component {

  constructor(props) {
    super(props);
    this.state = {};
    this.handleLeftChange = this.handleLeftChange.bind(this);
    this.handleRightChange = this.handleRightChange.bind(this);
    this.updateCar = this.updateCar.bind(this);
  }

  updateCar = (leftWheel, rightWheel) => {
    this.props.mutate({
      update: this.update,
      variables: {
        leftWheel: leftWheel,
        rightWheel: rightWheel
      }
    });
  }

  update = (store, mutation) => {
    const data = store.readQuery({ query: CarQuery });
    data.car = mutation.data.controlCar.car
    store.writeQuery({ query: CarQuery, data });
    this.setState({ leftWheel: data.car.leftWheel });
    this.setState({ rightWheel: data.car.rightWheel });
  }

  handleLeftChange = (event, leftSlider) => {
    let leftWheel = 2*(leftSlider-50);
    this.setState({ leftWheel: leftWheel });
    this.updateCar(leftWheel, this.state.rightWheel);
  }

  handleRightChange = (event, rightSlider) => {
    let rightWheel = 2*(rightSlider-50);
    this.setState({ rightWheel: rightWheel });
    this.updateCar(this.state.leftWheel, rightWheel);
  }

  componentWillReceiveProps = (props) => {
    // External props have changed (And have priority over graphql props)
    if (props.leftWheel !== undefined && props.rightWheel !== undefined){
      this.setState({
        leftWheel: props.leftWheel,
        rightWheel: props.rightWheel
      });
      this.updateCar(props.leftWheel, props.rightWheel);
    // GraphQL loaded props
    } else if (props.data.car){
      this.setState({
        leftWheel: props.data.car.leftWheel,
        rightWheel: props.data.car.rightWheel
      });
    }
  }

  render() {
    let { classes } = this.props;

    if (this.state.leftWheel===undefined || this.state.rightWheel==undefined){
      return <div>Loading</div>
    }

    // Calculate the slider values to show
    let leftWheel = this.state.leftWheel; //[-100, 100]
    let rightWheel = this.state.rightWheel; //[-100, 100]
    let leftSlider = (100+leftWheel)/2; //[0, 100]
    let rightSlider = (100+rightWheel)/2; //[0, 100]
    let disabled = this.props.disabled || false;

    return (
      <div>
        <Grid container spacing={24} alignItems="center">
          <Grid item xs={3} className={classes.root}></Grid>
          <Grid item xs={3} className={classes.root}>
            <Slider value={leftSlider} className={classes.slider} disabled={disabled} reversed onChange={this.handleLeftChange} vertical />
            <Typography align="center">{leftWheel.toFixed(1)}</Typography>
          </Grid>
          <Grid item xs={3} className={classes.root}>
            <Slider value={rightSlider} className={classes.slider} disabled={disabled} reversed onChange={this.handleRightChange} vertical />
            <Typography align="center">{rightWheel.toFixed(1)}</Typography>
          </Grid>
          <Grid item xs={3} className={classes.root}></Grid>
        </Grid>
      </div>
    );
  }
}

export default withStyles(styles)(Wheels);
