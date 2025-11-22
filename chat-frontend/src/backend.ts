import axios from "axios";

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