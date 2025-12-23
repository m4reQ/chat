import { useEffect, useState } from "react";
import { postConfirmEmail } from "../../backend.ts";
import { useParams, useSearchParams } from "react-router";

export default function ConfirmEmailPage({}) {
    const [params] = useSearchParams();
    const [confirmInProgress, setConfirmInProgress] = useState(true);

    useEffect(() => {
        postConfirmEmail(params.get("code") as string)
            .then(result => {
                // TODO Handle all cases of confirmation failure
                setConfirmInProgress(false);
            });
    },
    []);
    
    return confirmInProgress
        ? <span>Waiting...</span>
        : <span>Your email has been confirmed. Click <a href="/login">here</a> to log in.</span>;
}