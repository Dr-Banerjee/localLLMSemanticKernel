import { axiosClient } from "./axiosClient";
import type {
  ConversationMessage,
  ConversationSummariesQueryParams,
  ConversationSummaryResponse,
  ResponseToUserRequest,
  UserRequest,
} from "../types";

const DEFAULT_PAGE_SIZE = 12;

export async function fetchConversationSummaries(
  params: ConversationSummariesQueryParams,
): Promise<ConversationSummaryResponse> {
  const { data } = await axiosClient.get<ConversationSummaryResponse>("/conversations/summaries", {
    params: {
      page: params.page,
      pageSize: params.pageSize,
    },
  });
  return data;
}

export async function fetchConversationMessages(
  conversationId: number,
): Promise<ConversationMessage[]> {
  const { data } = await axiosClient.get<ConversationMessage[]>(
    `/conversations/${conversationId}/messages`,
  );
  return data;
}

export async function postConversationMessage(
  conversationId: number,
  userInput: string,
): Promise<ResponseToUserRequest> {
  const body: UserRequest = { userInput };
  const { data } = await axiosClient.post<ResponseToUserRequest>(
    `/conversations/${conversationId}/messages`,
    body,
  );
  return data;
}

export { DEFAULT_PAGE_SIZE };
