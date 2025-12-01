import NavbarButton from "./NavbarButton.tsx";
import "./Navbar.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { makeAPIRequest } from "../../../backend.ts";

export default function Navbar({}) {
    const navigate = useNavigate();
    const [currentSelectedButton, setCurrentSelectedButton] = useState(1);
    const [profilePictureURL, setProfilePictureURL] = useState<string>();

    useEffect(() => {
        const userJWT = localStorage.getItem("userJWT");
        if (userJWT === null) {
            navigate("/login");
            return;
        }

        makeAPIRequest({
            method: "get",
            url: "user",
            headers: {"Authorization": `Bearer ${userJWT}`}})
            .then(response => {
                console.log(response);
                if (response.status === 401) {
                    localStorage.removeItem("userJWT");
                    navigate("/login");
                    return;
                }
            });
        makeAPIRequest({
            method: "get",
            url: "user/profile-picture",
            headers: {"Authorization": `Bearer ${userJWT}`},
            responseType: "blob"})
            .then(response => {
                console.log(response);
                switch (response.status) {
                    case 401:
                        localStorage.removeItem("userJWT");
                        navigate("/login");
                        break;
                    case 200:
                        setProfilePictureURL(URL.createObjectURL(response.data));
                        break;
                    default:
                        console.error(response);
                }
            });
        
        return () => {
            if (profilePictureURL) {
                URL.revokeObjectURL(profilePictureURL);
            }
        }
    }, [])

    return <div className="navbar">
        <img src="assets/icons/app_icon.svg" />
        <div className="navbar-selector">
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_friends.svg"
                onClick={() => {setCurrentSelectedButton(0)}}
                isSelected={currentSelectedButton === 0} />
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_chat.svg"
                onClick={() => {setCurrentSelectedButton(1)}}
                isSelected={currentSelectedButton === 1} />
            <NavbarButton
                imgSrc="assets/icons/navbar_selector_add_friend.svg"
                onClick={() => {setCurrentSelectedButton(2)}}
                isSelected={currentSelectedButton === 2} />
        </div>
        <img
            className="navbar-profile-picture"
            src={profilePictureURL ?? "assets/icons/profile_picture_stub.svg"} />
    </div>
}