import type { ResponseToUserRequest, UserRequest } from "../types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  "",
);
const REQUEST_TIMEOUT_MS = 120_000;

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new ApiError("Pip ran into a wobbly answer. Let’s try again!", response.status);
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError("Pip is still thinking. Let’s try that question once more!");
    }

    throw new ApiError(
      "Pip couldn’t reach the teacher computer. Ask a grown-up to start the backend, then try again!",
    );
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export function sendConversationMessage(conversationId: number, userInput: string) {
  const body: UserRequest = { userInput };

  return requestJson<ResponseToUserRequest>(
    `/conversations/${conversationId}/messages`,
    {
      method: "POST",
      body: JSON.stringify(body),
    },
  );
}
