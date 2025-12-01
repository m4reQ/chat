import Navbar from "./components/Navbar.tsx";
import "./AppPage.css";
import ChatWindow from "./components/ChatWindow.tsx";

export default function AppPage({}) {
    return <div className="app-page-container">
        <Navbar />
        <div
            style={{
                marginTop: "1%",
                marginBottom: "1%",
                // height: "100%",
                flexGrow: 1,
                display: "flex",
                flexDirection: "row",
                }}>
            <div style={{width: "20%"}}></div>
            <ChatWindow />
            <div style={{width: "20%"}}></div>
        </div>
        
    </div>
}