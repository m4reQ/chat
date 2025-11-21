const path = require("path");
const webpack = require("webpack");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const CompressionWebpackPlugin = require("compression-webpack-plugin");
const WebpackObfuscator = require("webpack-obfuscator");

const isProduction = process.env.NODE_ENV === "production";

var plugins = [
    new CompressionWebpackPlugin(),
    new HtmlWebpackPlugin({
        template: path.resolve(__dirname, "public", "index.html"),
    }),
    new CopyWebpackPlugin({
        patterns: [
            {
                from: path.resolve(__dirname, "public"),
                to: path.resolve(__dirname, "dist"),
                filter: resourcePath => !resourcePath.endsWith("index.html"),
            },
        ],
    }),
    new webpack.DefinePlugin({
        "process.env": JSON.stringify({ ...process.env }),
    }),
];
if (isProduction) {
    plugins = [
        ...plugins,
        new WebpackObfuscator({
            rotateStringArray: true,
            stringArray: true,
            stringArrayThreshold: 0.75
        }),
    ];
}

module.exports = {
    entry: path.resolve(__dirname, "src/index.tsx"),
    plugins: plugins,
    devtool: "inline-source-map",
    output: {
        path: path.resolve(__dirname, "dist"),
        filename: "bundle.[contenthash].js",
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx|js|jsx)$/,
                include: path.resolve(__dirname, "src"),
                exclude: /node_modules/,
                use: [
                    {
                        loader: "babel-loader",
                        options: {
                            presets: [
                                [
                                    "@babel/preset-env",
                                    {
                                        targets: "defaults",
                                    },
                                ],
                                [
                                    "@babel/preset-react",
                                    {
                                        "runtime": "automatic"
                                    },
                                ],
                                [
                                    "@babel/preset-typescript",
                                ],
                            ],
                        },
                    },
                ],
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.(png|jpg|jpeg|gif|svg|ico|eot|ttf|woff|woff2)$/,
                type: "asset/resource",
            },
        ],
    },
    devServer: {
        static: path.resolve(__dirname, "public"),
        historyApiFallback: true,
        open: false,
        hot: false,
        port: 3000,
        liveReload: true,
        client: {
            overlay: true,
        },
        watchFiles: {
            paths: [
                "src/**/*.jsx",
                "src/**/*.tsx",
                "src/**/*.css",
                "public/**/*"],
            options: {
                usePolling: true,
            },
        },
    },
    mode: isProduction ? "production" : "development",
}