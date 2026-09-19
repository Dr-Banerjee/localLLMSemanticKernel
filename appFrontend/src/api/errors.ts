export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function messageForApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Something wobbled. Let’s try again in a moment!";
}
