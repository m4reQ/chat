import { useState } from "react";
import "./ContentSelector.css"

interface ContentSelectorProps {
    buttonHeaders: string[];
    onTabSelected: (arg0: number) => any;
}

export default function ContentSelector({
    buttonHeaders,
    onTabSelected}: ContentSelectorProps) {
    const [activeButtonIndex, setActiveButtonIndex] = useState(0);

    return <div className="content-selector-container">
        {buttonHeaders.map(
            (btnHeader, index, _) =>
                <button
                    key={index}
                    className="font-rest content-selector-button"
                    type="button"
                    style={{
                        backgroundColor: index !== activeButtonIndex
                            ? "#F1F1F1"
                            : "var(--start-page-select-option-bg-color)" }}
                    onClick={
                        (_) => {
                            onTabSelected(index);
                            setActiveButtonIndex(index); }}>
                    {btnHeader}
                </button>)}
    </div>;
}