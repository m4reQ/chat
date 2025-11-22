import { CSSProperties } from "react";
import "./CircularSpinner.css";

interface CircularSpinnerProps {
    style?: CSSProperties;
}

export default function CircularSpinner({style = undefined}: CircularSpinnerProps) {
    return <img
        src="assets/icons/circular_spinner.svg"
        className="circular-spinner"
        style={style}/>;
}