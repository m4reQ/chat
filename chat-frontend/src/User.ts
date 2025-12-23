import { makeAPIRequest, putRefreshUserActivity, putSetUserActivityStatus } from "./backend.ts";

const PROFILE_PICTURE_STUB_URL = "assets/icons/profile_picture_stub.svg";

export enum UserActivityStatus {
    ACTIVE = "ACTIVE",
    OFFLINE = "OFFLINE",
    BRB = "BRB",
    DONT_DISTURB = "DONT_DISTURB",
};

export interface UserData {
    id: number;
    username: string;
    email: string;
    created_at: Date;
    last_active: Date;
    activity_status: UserActivityStatus;
}

export class User {
    id: number;
    username: string;
    email: string;
    created_at: Date;
    last_active: Date;
    activity_status: UserActivityStatus;
    profilePictureURL: string;
    jwt: string;

    public static async fromJWT(jwt: string) {
        const userDataResponse = await makeAPIRequest({
            method: "GET",
            url: "/user",
            headers: {"Authorization": "Bearer " + jwt},
        });
        if (userDataResponse.status === 401) {
            return null;
        }

        const profilePictureURL = await getUserProfilePictureURL(jwt);
        if (profilePictureURL === null) {
            return null;
        }

        return new User(userDataResponse.data as UserData, profilePictureURL, jwt);
    }

    constructor(userData: UserData, profilePictureURL: string, jwt: string) {
        this.id = userData.id;
        this.username = userData.username;
        this.email = userData.email;
        this.created_at = userData.created_at;
        this.last_active = userData.last_active;
        this.activity_status = userData.activity_status;
        this.profilePictureURL = profilePictureURL;
        this.jwt = jwt;
    }

    public async setActivityStatus(status: UserActivityStatus) {
        const result = await putSetUserActivityStatus(this.jwt, status);
        if (result.status === 401) {
            return false;
        }

        this.activity_status = result.data.activity_status as UserActivityStatus;
        this.last_active = result.data.last_active as Date;
        return true;
    }

    public async refreshActivity() {
        const result = await putRefreshUserActivity(this.jwt);
        return result.status !== 401;
    }

    public invalidateProfilePicture() {
        if (this.profilePictureURL !== PROFILE_PICTURE_STUB_URL) {
            URL.revokeObjectURL(this.profilePictureURL);
        }
    }
}

async function getUserProfilePictureURL(jwt: string) {
    const response = await makeAPIRequest({
        method: "GET",
        url: "/user/profile-picture",
        headers: {"Authorization": "Bearer " + jwt},
        responseType: "blob",
    });

    switch (response.status) {
        case 401:
            return null;
        case 201:
            return PROFILE_PICTURE_STUB_URL;
    }

    // response.status === 200
    return URL.createObjectURL(response.data);
}