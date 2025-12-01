import * as CSS from "./NavbarButton.module.css";

interface NavbarButtonProps {
    imgSrc: string;
    onClick: () => any;
    isSelected: boolean;
}

export default function NavbarButton({
    imgSrc,
    onClick,
    isSelected}: NavbarButtonProps) {
    if (isSelected) {
        const [baseName, ext] = imgSrc.split(".");
        imgSrc = `${baseName}_active.${ext}`;
    }
    
    return <button
        onClick={onClick}
        className={CSS.selectorButton}>
        <img
            src={imgSrc}
            className={CSS.buttonImg}
            style={{
                backgroundColor: isSelected ? "#F6EAFF" : "transparent",
            }}/>
        <div
            className={CSS.buttonHighlightBar}
            style={{
                display: isSelected ? "initial" : "none"
            }}>
        </div>
    </button>
}