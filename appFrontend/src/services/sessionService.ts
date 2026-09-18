import { getUser, createSession } from "../api/client";
export class SessionService {
    async initialiseSession(){
        const response =await getUser();
        if (response.ok){
            return;
        }
        if (response.status !== 401){
            throw new Error("Failed to resolve current session");
        }
        const sessionResponse = await createSession();
        if (!sessionResponse.ok){
            throw new Error("Failed to create new session");
        }        
    }
}