import "./PageHeader.css";

interface PageHeader {
    headerText: string,
    subHeaderText: string,
}

export default function PageHeader({
    headerText,
    subHeaderText}: PageHeader) {
    return <div className="page-header-container">
        <div className="header">{headerText}</div>
        <div className="subheader font-rest">{subHeaderText}</div>
    </div>;
}