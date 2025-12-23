import AppWindow from "./AppWindow.tsx";
import * as CSS from "./ChatWindow.module.css";

export default function ChatWindow({}) {
    return <AppWindow
        width="60%"
        backgroundFilled>
        <div className={CSS.topBarContainer}>
            <span className={CSS.header}>Group Chat</span>
            <div className={CSS.topBarButtonsContainer}>
                <button>Messages</button>
                <button>Users</button>
            </div>
        </div>
    </AppWindow>;
}