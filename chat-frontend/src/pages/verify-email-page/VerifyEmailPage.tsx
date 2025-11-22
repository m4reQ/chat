import axios from "axios";
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";

interface VerifyEmailPageProps {
    onError: (retryAction: () => any) => any;
}

const STATUS_INITIAL = 0;
const STATUS_WAITING = 1;
const STATUS_ALREADY_VERIFIED = 2;
const STATUS_SUCCESS = 3;
const STATUS_FAILED = 4;

export default function VerifyEmailPage({ onError }: VerifyEmailPageProps) {
    const [searchParams, _] = useSearchParams();
    const [status, setStatus] = useState(STATUS_WAITING);
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const verificationCode = searchParams.get("code");
        if (!verificationCode) {
            navigate("/");
            return;
        }

        axios.request({
            url: `/auth/verify-email/${verificationCode}`,
            method: "post",
            baseURL: process.env.API_BASE_URL,
            headers: { "X-Api-Key": process.env.API_KEY },
            validateStatus: _ => true})
            .then(response => {
                switch (response.status) {
                    case 200:
                        setStatus(STATUS_SUCCESS);
                        break;
                    case 204:
                        setStatus(STATUS_ALREADY_VERIFIED);
                        break;
                    case 401:
                        setStatus(STATUS_FAILED);

                        switch (response.data.error_code) {
                            case "code_expired":
                                setErrorMessage("Verification code expired.");
                                break;
                            case "code_invalid":
                                setErrorMessage("Verification code is invalid.");
                                break;
                        }
                        
                        break;
                    case 404:
                        setStatus(STATUS_FAILED);
                        setErrorMessage("Account related to this verification code does not exist.");
                        break;
                    default:
                        setStatus(STATUS_INITIAL);
                        onError(() => {});
                }
            })
            .catch(error => {
                console.error(error);

                setStatus(STATUS_INITIAL);
                onError(() => {});
            });
    },
    []);

    switch (status) {
        case STATUS_INITIAL:
            return <></>;
        case STATUS_WAITING:
            return <h1>Waiting for verification...</h1>;
        case STATUS_ALREADY_VERIFIED:
            return <div style={{display: "flex", flexDirection: "column"}}>
                <h1>Email is already verified</h1>
                <a href="/login">Go to login</a>
            </div>;
        case STATUS_SUCCESS:
            return <div style={{display: "flex", flexDirection: "column"}}>
                <h1>Email verification success</h1>
                <a href="/login">Go to login</a>
            </div>;
        case STATUS_FAILED:
            return <>
                <h1>Email verification failed.</h1>
                <h2>{errorMessage}</h2>
            </>
        default:
            return <></>;
    }
}