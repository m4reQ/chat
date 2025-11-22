import { ReactNode } from "react";
import PageHeader from "./components/PageHeader.tsx";
import ContentSelector from "./components/ContentSelector.tsx";
import "./StartPage.css";
import { useLocation } from "react-router";

interface StartPageProps {
    content: {
        headerText: string;
        subHeaderText: string;
        mainElement: ReactNode};
};

export default function StartPage({content}: StartPageProps) {
    const location = useLocation();

    return <div className="start-page-container">
            <img src="assets/icons/app_logo.svg" className="start-page-logo" />
            <PageHeader
                headerText={content.headerText}
                subHeaderText={content.subHeaderText} />
            <div className="main-container">
                <ContentSelector currentPath={location.pathname} />
                <div className="page-content-container">
                    {content.mainElement}
                </div>
            </div>
        </div>;
}