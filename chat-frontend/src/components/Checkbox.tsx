import { ReactNode, useState } from "react";
import "./Checkbox.css";

interface CheckboxProps {
    id: string,
    label: ReactNode;
    required?: boolean;
    name?: string;
};

export default function Checkbox({
    id,
    label,
    required = false,
    name = undefined}: CheckboxProps) {
    const [checked, setChecked] = useState(false);

    return <div className="checkbox-container">
        <input
            type="checkbox"
            id={id}
            name={name}
            checked={checked}
            required={required}
            onChange={e => setChecked(e.target.checked)} />
        <label
            htmlFor={id}
            className="font-rest">
            {label}
        </label>
    </div>;
}