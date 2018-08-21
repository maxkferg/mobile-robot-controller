const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HashedModuleIdsPlugin = require('webpack/lib/HashedModuleIdsPlugin');

module.exports = {
    devtool: 'cheap-module-eval-source-map',
    entry: [
        'webpack-hot-middleware/client',
        './src/index',
    ],
    output: {
        publicPath: '/dist/',
    },

    devServer: {
        inline: false,
        contentBase: "./dist",
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
                NODE_ENV: '"development"',
            },
            __DEVELOPMENT__: true,
        }),
        new webpack.optimize.OccurrenceOrderPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new webpack.NoEmitOnErrorsPlugin(),
        new webpack.ProvidePlugin({
            jQuery: 'jquery',
        }),
    ],
};
