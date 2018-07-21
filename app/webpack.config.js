const path = require('path')

module.exports = {
    mode: 'production',
    entry: path.resolve(__dirname, 'js/robotLocus.js'),
    output: {
        path: path.resolve(__dirname, 'static/js'),
        filename: 'robotLocus.js'
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                use: [
                    {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                ['env', {'modules': false}]
                            ]
                        }
                    }
                ]
            }
        ]
    }
};
