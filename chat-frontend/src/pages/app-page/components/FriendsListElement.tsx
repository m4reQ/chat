import { useEffect, useState } from "react";
import * as CSS from "./FriendsListElement.css";
import { getUserProfilePictureURL } from "../../../backend";

interface FriendsListElementProps {
    userID: number;
    username: string;
    lastActive: Date;
};

export default function FriendsListElement({userID, username, lastActive}: FriendsListElementProps) {
    const [profilePictureURL, setProfilePictureURL] = useState<string>();

    useEffect(() => {
        getUserProfilePictureURL(userID)
            .then(url => {
                setProfilePictureURL(url);
            });
        
        return () => {
            if (profilePictureURL) {
                URL.revokeObjectURL(profilePictureURL);
            }
        }
    },
    [])
    return <div className={CSS.friendsListElement}>
        <img
            src={profilePictureURL ?? "assets/icons/profile_picture_stub.svg"}
            className={CSS.profilePictureImg}/>
    </div>;
}