import { CSSProperties, ReactNode } from "react";
import "./Button.css";

interface ButtonProps {
    label: ReactNode;
    isSubmitButton?: boolean;
    className?: string;
    style?: CSSProperties;
    onClick?: () => any;
};

export default function Button({
    label,
    onClick,
    isSubmitButton = false,
    className = undefined,
    style = undefined}: ButtonProps) {
    return <button
        type={isSubmitButton ? "submit" : undefined}
        className={`button-generic font-rest ${className}`}
        onClick={onClick?.()}
        style={style}>
        {label}
    </button>;
}