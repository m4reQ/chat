import { useState } from "react";
import "./TextField.css";

interface TextFieldProps {
    imgSrc: string;
    type: "text" | "password";
    name?: string;
    placeholder?: string;
    validateError?: string;
    onValueChange?: (newValue: string) => any;
};

export default function TextField({ 
    imgSrc,
    type = "text",
    name = undefined,
    placeholder = undefined,
    onValueChange = undefined,
    validateError = undefined}: TextFieldProps) {
    const [isPasswordVisible, setIsPasswordVisible] = useState(false);
    const [value, setValue] = useState<string>("");
        
    return <div className="text-field-wrapper">
        <img src={imgSrc} className="icon" />
        <div className="separator"></div>
        <div className="input-field-container">
            <input
                type={type === "password" && !isPasswordVisible
                        ? "password"
                        : "text"}
                className="input-field"
                name={name}
                value={value}
                placeholder=" "
                onChange={e => {
                    setValue(e.target.value);
                    onValueChange?.(e.target.value);
                }} />
            <span className="placeholder-label font-rest">{placeholder}</span>
        </div>
        {type === "password"
            ? <button
                type="button"
                onClick={_ => setIsPasswordVisible!(!isPasswordVisible)}>
                <img
                    className="show-password-icon"
                    src={isPasswordVisible
                        ? "/assets/icons/password_visible.svg"
                        : "/assets/icons/password_invisible.svg"} />
            </button>
            : null}
        {validateError !== undefined
            ? <div className="validate-icon-wrapper">
                <img
                    src={"assets/icons/validate_error_icon.svg"}
                    className="validate-icon" />
                <span className="validate-text">{validateError}</span>
              </div>
            : null }
    </div>;
}