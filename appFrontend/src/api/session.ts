import { axiosClient } from "./axiosClient";
import type { CurrentUser } from "../types";

export async function fetchCurrentUser(): Promise<CurrentUser> {
  const { data } = await axiosClient.get<CurrentUser>("/me");
  return data;
}

export async function createSession(): Promise<void> {
  await axiosClient.post("/session");
}
