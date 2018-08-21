import React, { Component } from 'react';
import { HttpLink } from 'apollo-link-http';
import { ApolloProvider } from 'react-apollo';
import { withStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

const TEST = false;
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
    margin: "auto",
    marginLeft: "auto",
    marginRight: "auto",
  },
  container: {
    display: "flex",
  },
};

class Accelerometer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      isRunning: false,
      isEnabled: false
    };
    this.count = 0;
    this.handleClick = this.handleClick.bind(this);
    this.handleOrientation = this.handleOrientation.bind(this);

    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', this.handleOrientation, false);
      this.state.isEnabled = true;
    }

    // Test
    if (TEST){
      console.log("Accelerometer test mode");
      let self = this;
      self.state.isEnabled = true;
      self.c = setInterval(function(){
        let beta = 180*Math.random()-90;
        let gamma = 180*Math.random()-90;
        let event = {beta: beta, gamma: gamma};
        self.handleOrientation(event);
      }, 20);
    }
  }

  handleOrientation(event){
    if (!this.state.isRunning) return;
    this.count += 1;
    if (this.count % 100 > 0) return;
    this.props.onMove(event);
    console.log(event);
  }

  handleClick(){
    this.setState({isRunning: !this.state.isRunning});
  }

  componentWillUnmount() {
    if (this.c){
      clearInterval(this.c);
    }
  }

  render() {
    let { classes } = this.props;
    let message = "Start";
    let color = "primary";

    if (this.state.isRunning){
      message = "Stop";
      color = "secondary";
    }

    return (
      <div className={classes.container}>
        <Button
          variant="contained"
          disabled={!this.state.isEnabled}
          onClick={this.handleClick}
          color={color}
          className={classes.button}>
          {message}
        </Button>
      </div>
    );
  }
}

export default withStyles(styles)(Accelerometer);
