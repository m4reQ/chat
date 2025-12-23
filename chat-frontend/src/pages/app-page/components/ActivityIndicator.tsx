import * as CSS from "./ActivityIndicator.module.css";

export type ColorString = `#${string}`;

interface ActivityIndicatorProps {
    color: ColorString;
}

export default function ActivityIndicator({color}: ActivityIndicatorProps) {
    return <div
        className={CSS.activityIndicator}
        style={{backgroundColor: color}}>
    </div>;
}