export class ApiError extends Error {
  override name = "ApiError";
  readonly detail?: string;

  constructor(
    message: string,
    readonly status?: number,
    options?: ErrorOptions,
    detail?: string,
  ) {
    super(message, options);
    this.detail = detail;
  }
}

export function messageForApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  return "Something wobbled. Let’s try again in a moment!";
}
