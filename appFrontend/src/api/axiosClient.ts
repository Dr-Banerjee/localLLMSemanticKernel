import axios, { AxiosError, HttpStatusCode, isAxiosError } from "axios";
import { ApiError } from "./errors";

declare module "axios" {
  interface AxiosRequestConfig {
    _retried?: boolean;
  }
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");

if (!API_BASE_URL) {
  throw new Error("VITE_API_BASE_URL is not configured");
}
const REQUEST_TIMEOUT_MS = 120_000;

export const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT_MS,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (isAxiosError(error)) {
    if (error.code === AxiosError.ECONNABORTED || error.code === AxiosError.ETIMEDOUT) {
      return new ApiError("Pip is still thinking. Let’s try that question once more!");
    }

    if (error.response) {
      return new ApiError("Pip ran into a wobbly answer. Let’s try again!", error.response.status);
    }

    return new ApiError(
      "Pip couldn’t reach the teacher computer. Ask a grown-up to start the backend, then try again!",
    );
  }

  return new ApiError("Something wobbled. Let’s try again in a moment!");
}

axiosClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!isAxiosError(error)) {
      return Promise.reject(toApiError(error));
    }

    const config = error.config;
    const requestUrl = config?.url ?? "";
    const isSessionRequest = requestUrl.includes("/session");

    if (
      error.response?.status === HttpStatusCode.Unauthorized &&
      config &&
      !config._retried &&
      !isSessionRequest
    ) {
      config._retried = true;
      try {
        await axiosClient.post("/session");
        return axiosClient.request(config);
      } catch (sessionError) {
        return Promise.reject(toApiError(sessionError));
      }
    }

    return Promise.reject(toApiError(error));
  },
);
