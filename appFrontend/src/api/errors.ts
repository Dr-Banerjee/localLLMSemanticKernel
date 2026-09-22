export class ApiError extends Error {
  override name = "ApiError";

  constructor(
    message: string,
    readonly status?: number,
    options?: ErrorOptions,
  ) {
    super(message, options);
  }
}

export function messageForApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Something wobbled. Let’s try again in a moment!";
}
