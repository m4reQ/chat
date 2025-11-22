import { useEffect } from "react";
import { useNavigate } from "react-router";

export default function IndexPage({}) {
    const navigate = useNavigate();

    useEffect(() => {
        if (!localStorage.getItem("userJWT")) {
            navigate("/login", {replace: true});
        } else {
            navigate("/app", {replace: true});
        }
    });
    
    return <></>;
}