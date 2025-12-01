import * as CSS from "./ChatWindow.module.css";

export default function ChatWindow({}) {
    return <div className={CSS.container}>
        <div className={CSS.topBarContainer + " font-rest"}>
            <h1>Group Chat</h1>
            <div className={CSS.topBarButtonsContainer}>
                <button>Messages</button>
                <button>Users</button>
            </div>
        </div>
        
    </div>
}