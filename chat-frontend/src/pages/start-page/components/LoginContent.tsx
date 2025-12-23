import { useEffect, useState } from "react";
import TextField from "./TextField.tsx";
import axios from "axios";
import "./LoginContent.css";
import Checkbox from "../../../components/Checkbox.tsx";
import Link from "../../../components/Link.tsx";
import Button from "../../../components/Button.tsx";
import { useNavigate } from "react-router";
import { LoginResult, postLoginRequest } from "../../../backend.ts";

interface LoginContentProps {
    onError: (retryAction: () => any) => any;
};

export function LoginContent({onError}: LoginContentProps) {
    const [isLoginInProgress, setIsLoginInProgress] = useState(false);
    const [usernameValidateError, setUsernameValidateError] = useState<string | undefined>(undefined);
    const [passwordValidateError, setPasswordValidateError] = useState<string | undefined>(undefined);
    const navigate = useNavigate();

    async function onLogin(formData: FormData) {
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

        var loginResult: LoginResult;
        var accessToken: string | null;
        try {
            var [loginResult, accessToken] = await postLoginRequest(username, password);
        } catch (error) {
            console.log(error);
            onError(() => {});
            setIsLoginInProgress(false);
            return;
        }

        switch (loginResult) {
            case LoginResult.SUCCESS:
                localStorage.setItem("userJWT", accessToken as string);
                navigate("/app");
                break;
            case LoginResult.INVALID_CREDENTIALS:
                setPasswordValidateError("Invalid password for the given username!");
                break;
            case LoginResult.UNAUTHORIZED_CLIENT:
                setUsernameValidateError("Please verify your account by using link sent to Your email, before login.");
                break;
            case LoginResult.INTERNAL_ERROR:
                onError(() => {});
        }

        setIsLoginInProgress(false);
    }

    useEffect(() => {
        if (localStorage.getItem("userJWT")) {
            navigate("/app");
        }
    },
    []);

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
            label="Save login info" />
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