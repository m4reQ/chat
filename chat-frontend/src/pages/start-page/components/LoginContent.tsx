import { useState } from "react";
import TextField from "./TextField.tsx";
import axios from "axios";
import "./LoginContent.css";
import Checkbox from "../../../components/Checkbox.tsx";
import Link from "../../../components/Link.tsx";
import Button from "../../../components/Button.tsx";

interface LoginContentProps {
    onError: (retryAction: () => any) => any;
};

export function LoginContent({onError}: LoginContentProps) {
    const [isLoginInProgress, setIsLoginInProgress] = useState(false);
    const [usernameValidateError, setUsernameValidateError] = useState<string | undefined>(undefined);
    const [passwordValidateError, setPasswordValidateError] = useState<string | undefined>(undefined);
    const [saveLoginInfoChecked, setSaveLoginInfoChecked] = useState(false);

    function sendLoginRequest(username: string, password: string) {
        const retryAction = () => sendLoginRequest(username, password);

        axios.request({
            url: "/auth/login",
            method: "post",
            baseURL: process.env.API_BASE_URL,
            data: {
                grant_type: "password",
                username: username,
                password: password },
            headers: {
                "X-Api-Key": process.env.API_KEY,
                "Content-Type": "application/x-www-form-urlencoded" },
            validateStatus: _ => true })
            .then(response => {
                setIsLoginInProgress(false);

                switch (response.status) {
                    case 200:
                        // TODO Redirect to main
                        break;
                    case 401:
                        setPasswordValidateError("Invalid password for the given username!");
                        break;
                    case 400:
                        if (response.data.error === "unauthorized_client") {
                            // TODO Redirect to email not validated
                        } else {
                            onError(retryAction);
                        }

                        break;
                    default:
                        onError(retryAction);
                }
            })
            .catch(error => {
                setIsLoginInProgress(false);
                onError?.(retryAction);
            });
    }

    function onLogin(formData: FormData) {
        setIsLoginInProgress(true);

        const username = formData.get("username") as string;
        const password = formData.get("password") as string;

        let anyValueInvalid = false;

        if (!username) {
            setUsernameValidateError("Username cannot be empty!");
            anyValueInvalid = true;
        } else {
            setUsernameValidateError(undefined);
        }

        if (!password) {
            setPasswordValidateError("Password cannot be empty!");
            anyValueInvalid = true;
        } else {
            setPasswordValidateError(undefined);
        }

        if (anyValueInvalid) {
            setIsLoginInProgress(false);
            return;
        }

        sendLoginRequest(username, password);
    }

    return <form style={{all: "inherit"}} action={onLogin}>
        <TextField
            name="username"
            type="text"
            imgSrc="assets/icons/username_input.svg"
            placeholder="Username"
            validateError={usernameValidateError}/>
        <TextField
            name="password"
            type="password"
            imgSrc="assets/icons/password_input.svg"
            placeholder="Password"
            validateError={passwordValidateError}/>
        <Checkbox
            name="saveInfo"
            id="save-login-info-checkbox"
            label="Save login info"
            isChecked={saveLoginInfoChecked}
            onChecked={setSaveLoginInfoChecked} />
        <Button
            label="Continue"
            isSubmitButton
            className="login-button"
            style={{
                backgroundColor: isLoginInProgress 
                    ? "var(--start-page-select-option-disabled-color)"
                    : "var(--start-page-accent-color)",
            }}/>
        <Link
            text="Reset your password"
            url="/reset-password"
            className="reset-password-link"/>
    </form>;
}