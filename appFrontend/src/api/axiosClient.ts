import axios, { AxiosError, HttpStatusCode, isAxiosError } from "axios";
import i18n from "../i18n";
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

function responseDetail(error: AxiosError): string | undefined {
  const data = error.response?.data;
  if (typeof data !== "object" || data === null || !("detail" in data)) {
    return undefined;
  }
  return typeof data.detail === "string" ? data.detail : undefined;
}

function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (isAxiosError(error)) {
    if (error.code === AxiosError.ECONNABORTED || error.code === AxiosError.ETIMEDOUT) {
      return new ApiError(i18n.t("errors.timeout"));
    }

    if (error.response) {
      const detail = responseDetail(error);
      return new ApiError(
        i18n.t("errors.wobblyAnswer"),
        error.response.status,
        undefined,
        detail,
      );
    }

    return new ApiError(
      i18n.t("errors.offline"),
    );
  }

  return new ApiError(i18n.t("errors.wobbled"));
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
        await axiosClient.post("/api/sessions/session");
        return axiosClient.request(config);
      } catch (sessionError) {
        return Promise.reject(toApiError(sessionError));
      }
    }

    return Promise.reject(toApiError(error));
  },
);
