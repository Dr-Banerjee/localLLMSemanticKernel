import { axiosClient } from "./axiosClient";
import type {
  ConversationMessage,
  ConversationSummariesQueryParams,
  ConversationSummaryResponse,
  ResponseToUserRequest,
  UserRequest,
} from "../types";

export const DEFAULT_PAGE_SIZE = 12;

type RequestOptions = {
  signal?: AbortSignal;
};

export async function fetchConversationSummaries(
  params: ConversationSummariesQueryParams,
  { signal }: RequestOptions = {},
): Promise<ConversationSummaryResponse> {
  const { data } = await axiosClient.get<ConversationSummaryResponse>("/conversations/summaries", {
    params,
    signal,
  });
  return data;
}

export async function fetchConversationMessages(
  conversationId: number,
  { signal }: RequestOptions = {},
): Promise<ConversationMessage[]> {
  const { data } = await axiosClient.get<ConversationMessage[]>(
    `/conversations/${conversationId}/messages`,
    { signal },
  );
  return data;
}

export async function postConversationMessage(
  conversationId: number,
  userInput: string,
  { signal }: RequestOptions = {},
): Promise<ResponseToUserRequest> {
  const body: UserRequest = { userInput };
  const { data } = await axiosClient.post<ResponseToUserRequest>(
    `/conversations/${conversationId}/messages`,
    body,
    { signal },
  );
  return data;
}
