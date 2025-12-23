import { useQuery } from "react-query";
import { UserChatRoom } from "../../../models/ChatRoom.ts";
import { makeAPIRequest } from "../../../backend.ts";
import * as CSS from "./ChatRoomListItem.module.css";

interface ChatRoomListItemProps {
    room: UserChatRoom;
    isSelected: boolean;
    onSelect: () => any;
};

async function getChatRoomImageURL(roomID: number) {
    const response = await makeAPIRequest({
        method: "GET",
        url: `/room/${roomID}/image`,
        responseType: "blob",
    });
    return response.status == 200
        ? URL.createObjectURL(response.data)
        : undefined;
}

export default function ChatRoomListItem({ room, isSelected, onSelect }: ChatRoomListItemProps) {
    const imageQuery = useQuery(
        ["chat-room-image", room.id],
        () => getChatRoomImageURL(room.id));

    return <button
        className={CSS.item}
        onClick={e => {
            e.preventDefault();
            onSelect();
        }}
        style={{
            backgroundColor: isSelected ? "#F4F4F4" : "transparent",
        }}>
        <img
            className={CSS.icon}
            src={imageQuery.isSuccess && imageQuery.data
                ? imageQuery.data
                : "/assets/icons/profile_picture_stub.svg"} />
        <div className={CSS.inner}>
            <span className={CSS.text}>{room.name}</span>
            <span className={`${CSS.text} ${CSS.auxText}`}>Last message</span>
        </div>
        <span className={CSS.auxText}>21:37</span>
    </button>
}