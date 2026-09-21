import { axiosClient } from "./axiosClient";
import type { CurrentUser } from "../types";

type RequestOptions = {
  signal?: AbortSignal;
};

export async function fetchCurrentUser({ signal }: RequestOptions = {}): Promise<CurrentUser> {
  const { data } = await axiosClient.get<CurrentUser>("/me", { signal });
  return data;
}

export async function createSession({ signal }: RequestOptions = {}): Promise<void> {
  await axiosClient.post("/session", undefined, { signal });
}
