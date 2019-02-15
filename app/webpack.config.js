const path = require('path')

module.exports = {
    mode: 'production',
    target: 'web',
    entry: ['@babel/polyfill', path.resolve(__dirname, 'js/robotLocus.js')],
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: 'robotLocus.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    }
};
