var path = require('path')
var webpack = require('webpack')
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {

    context: __dirname,

    entry: {
      buildList: './assets/js/build-list.jsx',
      buildRebuild: './assets/js/build-rebuild.jsx',
      buildStatus: './assets/js/build-status.jsx',
      buildDetail: './assets/js/build-detail.jsx'
    },

    output: {
        path: path.resolve('./assets/bundles/'),
        filename: '[name]-[hash].js'
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        })
    ],

    module: {
        loaders: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {presets: ['react']}
            }
        ]
    },

    resolve: {
        modules: ['node_modules'],
        extensions: ['.js', '.jsx']
    }
 
}
