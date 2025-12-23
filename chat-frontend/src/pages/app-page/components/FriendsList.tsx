import { useEffect, useState } from "react";
import { User } from "../../../User";

interface FriendsListProps {
    user: User;
}

interface FriendEntry {
    user_id: number;
    username: string;
    last_active: Date;
}

export default function FriendsList({user}: FriendsListProps) {
    const [friends, setFriends] = useState([]);

    useEffect({
        await user.getFriendsList()
    },
    friends);

    return <div
        style={{
            display: "flex",
            flexDirection: "column",
        }}>

    </div>;
}