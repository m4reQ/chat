const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const WebpackObfuscator = require("webpack-obfuscator");

const isProduction = process.env.NODE_ENV === "production";

var plugins = [
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
];
if (!isProduction) {
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
    entry: "./src/index.tsx",
    output: {
        path: path.resolve(__dirname, "dist"),
        filename: "bundle.[contenthash].js",
        clean: true,
    },
    resolve: {
        extensions: [".tsx", ".ts", ".js"],
    },
    module: {
        rules: [
            {
                test: /\.(ts|tsx|js|jsx)$/,
                exclude: /node_modules/,
                use: "babel-loader",
            },
            {
                test: /\.module\.css$/,
                use: [
                    "style-loader",
                    {
                        loader: "css-loader",
                        options: { modules: true },
                    },
                ],
            },
            {
                test: /\.css$/,
                exclude: /\.module\.css$/,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.(png|jpg|jpeg|gif|svg|ico|eot|ttf|woff|woff2)$/,
                type: "asset/resource",
            },
        ],
    },
    plugins: plugins,
    devServer: {
        static: path.resolve(__dirname, "public"),
        historyApiFallback: true,
        open: true,
        hot: true,
        port: 3000,
    },
    mode: isProduction ? "production" : "development",
}