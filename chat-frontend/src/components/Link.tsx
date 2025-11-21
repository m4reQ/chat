import { CSSProperties } from "react";
import "./Link.css";

interface LinkProps {
    text: string;
    url: string;
    className?: string;
    style?: CSSProperties;
};

export default function Link({
    text,
    url,
    className = undefined,
    style = undefined}: LinkProps) {
    return <a
        href={url}
        className={`font-rest link ${className ?? ""}`}
        style={style}>
        {text}
    </a>;
}