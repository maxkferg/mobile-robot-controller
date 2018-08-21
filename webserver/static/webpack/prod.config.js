const webpack = require('webpack');

module.exports = {
    devtool: 'source-map',

    output: {
        publicPath: 'dist/',
    },

    module: {
        rules: [{
          test: /\.css$/,
          exclude: [/node_modules/],
          use: [{
              loader: "style-loader" // creates style nodes from JS strings
          },{
              loader: "css-loader" // translates CSS into CommonJS
          },{
              loader: "sass-loader" // compiles Sass to CSS
          }]
        },{
          test: /\.scss$/,
          exclude: [/node_modules/],
          use: [{
              loader: "style-loader" // creates style nodes from JS strings
          },{
              loader: "css-loader" // translates CSS into CommonJS
          },{
              loader: "sass-loader" // compiles Sass to CSS
          }]
        }]
    },

    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: '"production"',
            },
            __DEVELOPMENT__: false,
        }),
        new webpack.optimize.OccurrenceOrderPlugin(),
    ],
};
