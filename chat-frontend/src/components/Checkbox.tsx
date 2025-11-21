import { ReactNode } from "react";
import "./Checkbox.css";

interface CheckboxProps {
    id: string,
    label: ReactNode;
    isChecked: boolean;
    name?: string,
    onChecked: (isChecked: boolean) => any;
};

export default function Checkbox({
    id,
    label,
    isChecked,
    onChecked,
    name = undefined}: CheckboxProps) {
    return <div className="checkbox-container">
        <input
            type="checkbox"
            id={id}
            name={name}
            checked={isChecked}
            onChange={e => onChecked(e.target.checked)} />
        <label
            htmlFor={id}
            className="font-rest">
            {label}
        </label>
    </div>;
}