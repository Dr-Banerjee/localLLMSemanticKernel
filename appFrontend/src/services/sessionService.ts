import { fetchCurrentUser } from "../api/session";

export class SessionService {
  async initialiseSession(): Promise<void> {
    await fetchCurrentUser();
  }
}
