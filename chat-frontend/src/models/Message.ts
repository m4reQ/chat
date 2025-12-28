export enum MessageType {
    Text = "TEXT",
    Image = "IMAGE",
    File = "FILE",
};

export interface Message {
    id: number;
    type: MessageType;
    content: string;
    sent_at: Date;
    sender_id: number;
    sender_username: string;
};