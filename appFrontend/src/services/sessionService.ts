import { fetchCurrentUser } from "../api/session";

export class SessionService {
  async initialiseSession(signal?: AbortSignal): Promise<void> {
    await fetchCurrentUser({ signal });
  }
}
