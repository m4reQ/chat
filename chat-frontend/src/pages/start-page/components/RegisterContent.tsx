import { useState } from "react";
import Checkbox from "../../../components/Checkbox.tsx";
import TextField from "./TextField.tsx";
import Link from "../../../components/Link.tsx";
import Button from "../../../components/Button.tsx";
import { getPasswordValidationRules, postRegisterRequest, RegisterResult } from "../../../backend.ts";
import "./RegisterContent.css";
import axios from "axios";

interface RegisterContentProps {
    onError: (retryAction: () => any) => any;
}

export default function RegisterContent({onError}: RegisterContentProps) {
    const [registerInProgress, setRegisterInProgress] = useState(false);
    const [usernameValidateError, setUsernameValidateError] = useState<string | undefined>(undefined);
    const [emailValidateError, setEmailValidateError] = useState<string | undefined>(undefined);
    const [passwordValidateError, setPasswordValidateError] = useState<string | undefined>(undefined);
    const [passwordRepeatValidateError, setPasswordRepeatValidateError] = useState<string | undefined>(undefined);

    async function onRegister(formData: FormData) {
        setRegisterInProgress(true);

        const username = formData.get("username") as string;
        const email = formData.get("email") as string;
        const password = formData.get("password") as string;
        const passwordRepeat = formData.get("passwordRepeat") as string;

        let anyValueInvalid = false;

        if (!username) {
            setUsernameValidateError("Username cannot be empty!");
            anyValueInvalid = true;
        } else {
            setUsernameValidateError(undefined);
        }
        
        // TODO Use input[type=email] for email input
        if (!email) {
            setEmailValidateError("E-mail address cannot be empty!");
            anyValueInvalid = true;
        } else {
            setEmailValidateError(undefined);
        }

        const passwordsMatch = password === passwordRepeat;

        if (!passwordsMatch) {
            setPasswordValidateError("Passwords do not match!");
            setPasswordRepeatValidateError("Passwords do not match!");
            anyValueInvalid = true;
        } else {
            setPasswordValidateError(undefined);
            setPasswordRepeatValidateError(undefined);
        }

        if (!password) {
            setPasswordValidateError("Password cannot be empty!");
            anyValueInvalid = true;
        } else if (password && passwordsMatch) {
            setPasswordValidateError(undefined);
        }

        if (!passwordRepeat) {
            setPasswordRepeatValidateError("Password repeat cannot be empty!");
            anyValueInvalid = true;
        } else if (passwordRepeat && passwordsMatch) {
            setPasswordRepeatValidateError(undefined);
        }
        
        const [regex, minPasswordLength] = await getPasswordValidationRules();
        if (!regex.test(password)) {
            setPasswordValidateError(`Password must be at least ${minPasswordLength} characters long and contain at least: one capital letter, one number and one special character.`);
            anyValueInvalid = true;
        } else {
            setPasswordValidateError(undefined);
        }

        if (anyValueInvalid) {
            setRegisterInProgress(false);
            return;
        }

        var registerResult: RegisterResult;
        try {
            registerResult = await postRegisterRequest(username, email, password);
        } catch (error) {
            console.error(error);
            onError(() => {});
            setRegisterInProgress(false);
            return;
        }
        
        switch (registerResult) {
            case RegisterResult.INVALID_ENCODING:
                setPasswordValidateError("Password must only include UTF-8 characters.");
                break;
            case RegisterResult.ALREADY_EXISTS:
                setEmailValidateError("User with provided email or username already exists.");
                setUsernameValidateError("User with provided email or username already exists.");
                break;
            case RegisterResult.PASSWORD_INVALID:
                setPasswordValidateError("Password format is invalid.");
                break;
            case RegisterResult.EMAIL_INVALID:
                setEmailValidateError("Provided email address is invalid.");
                break;
            case RegisterResult.EMAIL_DOESNT_EXIST:
                setEmailValidateError("Provided email address doesn't exist.");
                break;
            case RegisterResult.INTERNAL_ERROR:
                onError(() => {});
                break;
            default:
                // TODO Show popup indicating that user was registered successfully.
        }

        setRegisterInProgress(false);
    }

    return <form className="register-form" action={onRegister}>
        <TextField
            type="text"
            name="username"
            placeholder="Your username"
            imgSrc="assets/icons/username_input.svg"
            validateError={usernameValidateError}/>
        <TextField
            type="text"
            name="email"
            placeholder="Your email address"
            imgSrc="assets/icons/email_input.svg"
            validateError={emailValidateError}/>
        <TextField
            name="password"
            placeholder="Your password"
            imgSrc="assets/icons/password_input.svg"
            type="password"
            validateError={passwordValidateError}/>
        <TextField
            name="passwordRepeat"
            placeholder="Confirm your password"
            imgSrc="assets/icons/password_input.svg"
            type="password"
            validateError={passwordRepeatValidateError}/>
        <Checkbox
            id="tos-checkbox"
            name="tos-checkbox"
            label={<span>
                By signing up, You agree to the <Link text="Terms of Service" url="/tos"/> and <Link text="Privacy Policy" url="/privacy-policy" />
            </span>}
            required/>
        <Button
            isSubmitButton
            label="Create account"
            className="register-button"
            style={{
                backgroundColor: registerInProgress
                    ? "var(--start-page-select-option-disabled-color)"
                    : "var(--start-page-accent-color)",
            }}/>
        <div className="already-member-container">
            <span className="font-rest already-member-label">Already a member?</span>
            <Link
                text="Click here to log in"
                url="/login"
                className="login-link"/>
        </div>
    </form>;
}