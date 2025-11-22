import { useState } from "react";
import "./ContentSelector.css"
import { useNavigate } from "react-router";

interface ButtonData {
    text: string;
    redirectPath: string;
};

interface ContentSelectorProps {
    currentPath: string;
}

export default function ContentSelector({
    currentPath}: ContentSelectorProps) {
    const navigate = useNavigate();

    const buttonsData: ButtonData[] = [
        {text: "Sign In", redirectPath: "/login"},
        {text: "Sign Up", redirectPath: "/register"},
    ];

    return <div className="content-selector-container">
        {buttonsData.map(
            ({text, redirectPath}, index, _) =>
                <button
                    key={index}
                    className="font-rest content-selector-button"
                    type="button"
                    style={{
                        backgroundColor: currentPath !== redirectPath
                            ? "#F1F1F1"
                            : "var(--start-page-select-option-bg-color)" }}
                    onClick={_ => navigate(redirectPath) }>
                    {text}
                </button>)}
    </div>;
}