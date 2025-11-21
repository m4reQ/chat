import { ReactNode, useState } from "react";
import PageHeader from "./components/PageHeader.tsx";
import ContentSelector from "./components/ContentSelector.tsx";
import { LoginContent } from "./components/LoginContent.tsx";
import RegisterContent from "./components/RegisterContent.tsx";
import "./StartPage.css";
import { useLocation } from "react-router";

interface StartPageProps {
    onError: (retryAction: () => any) => any,
};

interface Tab {
    headerText: string;
    subHeaderText: string;
    tabContent: ReactNode;
};

export default function StartPage({
    onError,
    }: StartPageProps) {
    const tabs: Tab[] = [
        {headerText: "Welcome Back",
         subHeaderText: "Hello, please enter your login details",
         tabContent: <LoginContent onError={onError} />},
        {headerText: "Create account",
         subHeaderText: "Hi, please enter details for your new account",
         tabContent: <RegisterContent onError={onError} />},
    ]

    const location = useLocation();
    const [currentTab, setCurrentTab] = useState<Tab>(location.pathname === "/login" ? tabs[0] : tabs[0]);

    return <div className="start-page-container">
            <img src="assets/icons/app_logo.svg" className="start-page-logo" />
            <PageHeader
                headerText={currentTab.headerText}
                subHeaderText={currentTab.subHeaderText} />
            <div className="main-container">
                <ContentSelector
                    buttonHeaders={["Sign In", "Signup"]}
                    onTabSelected={idx => setCurrentTab(tabs[idx])} />
                <div className="page-content-container">
                    {currentTab.tabContent}
                </div>
            </div>
        </div>;
}