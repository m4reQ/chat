import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import * as CSS from "./ActivityStatusSelector.module.css";

export interface ActivityStatusSelectorItem {
    statusText: string;
    selectorBackgroundColor: string;
    selectorStrokeColor: string;
}

interface ActivityStatusSelectorProps {
    items: ActivityStatusSelectorItem[];
    onSelect?: (index: number) => any;
    initialIndex?: number;
}

interface ActivityStatusButtonProps {
    color: string;
    bgColor: string;
    statusText: string;
    onClick: () => any;
    showExpandIcon?: boolean;
    isExpanded?: boolean;
}

function ActivityStatusButton({color, bgColor, statusText, onClick, showExpandIcon = false, isExpanded = false}: ActivityStatusButtonProps) {
    return <button
        className={CSS.expandButton}
        style={{
            backgroundColor: bgColor,
        }}
        onClick={onClick}>
        <span style={{color: color}}>{statusText}</span>
        {showExpandIcon
            ? <svg
                xmlns="http://www.w3.org/2000/svg"
                className={CSS.expandIcon}
                style={{
                    rotate: isExpanded ? "180deg" : "0deg"
                }}
                fill="none"
                viewBox="0 0 24 24"
                stroke={color}>
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M19 9l-7 7-7-7" />
            </svg>
            : null}
    </button>;
}

export default function ActivityStatusSelector({items, onSelect = undefined, initialIndex = 0}: ActivityStatusSelectorProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [selectedIndex, setSelectedIndex] = useState(initialIndex);
    const containerRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        document.addEventListener(
            "mousedown",
            (e) => {
                if (containerRef.current && !containerRef.current.contains(e.target as (Node | null))) {
                    setIsExpanded(false);
                }
            });
    },
    []);

    useEffect(() => {
        onSelect?.(selectedIndex);
    },
    [selectedIndex]);

    const selectedItem = items[selectedIndex];
    return <div
        ref={containerRef}
        className={CSS.container} >
        <ActivityStatusButton
            color={selectedItem.selectorStrokeColor}
            bgColor={selectedItem.selectorBackgroundColor}
            statusText={selectedItem.statusText}
            onClick={() => setIsExpanded((s) => !s)}
            isExpanded={isExpanded}
            showExpandIcon/>
        <AnimatePresence>
            {isExpanded
                ? <motion.ul
                    role="listbox"
                    id="activity-status-listbox"
                    initial={{opacity: 0, height: 0}}
                    animate={{opacity: 1, height: "auto"}}
                    exit={{opacity: 0, height: 0}}
                    style={{willChange: "height", padding: 0, marginTop: 0, position: "absolute", background: "white", width: "100%"}}>
                    {items.map((x, idx) => 
                        idx !== selectedIndex
                            ? <li
                                key={idx}
                                id={`activity-status-item-${idx}`}
                                role="option"
                                className={CSS.statusSelectorListItem}>
                                <ActivityStatusButton 
                                    color={x.selectorStrokeColor}
                                    bgColor={x.selectorBackgroundColor}
                                    statusText={x.statusText}
                                    onClick={() => {
                                        setSelectedIndex(idx);
                                        setIsExpanded(false);
                                    }} />
                            </li>
                            : null)}
                </motion.ul>
                : null}
        </AnimatePresence>
    </div>
}