import axios from "axios";

interface MakeBackendRequestProps {
    endpoint: string;
    method: "post" | "get" | "put",

}

function makeBackendRequest({
    endpoint,
    method = "get",
    
    }: MakeBackendRequestProps) {
    const baseURL = process.env.API_BASE_URL;
    const apiKey = process.env.API_KEY;

    return axios.request({

    })
}