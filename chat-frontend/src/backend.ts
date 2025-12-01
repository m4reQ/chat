import axios, { AxiosHeaders, Method, RawAxiosRequestHeaders, ResponseType } from "axios";

export async function getPasswordValidationRules(): Promise<[RegExp, number]> {
    const response = await axios.request({
        url: "/auth/password-validation-rules",
        method: "get",
        baseURL: process.env.API_BASE_URL,
        headers: { "X-Api-Key": process.env.API_KEY },
        validateStatus: _ => true });
    if (response.status === 200) {
        return [
            new RegExp(response.data.regex),
            response.data.min_password_length];
    }

    throw new Error("Failed to get password validation rules.");
}

interface RequestConfig {
    method: Method,
    url: string,
    headers?: RawAxiosRequestHeaders | AxiosHeaders,
    responseType?: ResponseType,
};

export function makeAPIRequest({
    method,
    url,
    headers = undefined,
    responseType = "json"}: RequestConfig) {
    return axios.request({
        baseURL: process.env.API_BASE_URL,
        validateStatus: _ => true,
        method: method,
        url: url,
        responseType: responseType,
        headers: {
            "X-Api-Key": process.env.API_KEY,
            ...headers}});
}