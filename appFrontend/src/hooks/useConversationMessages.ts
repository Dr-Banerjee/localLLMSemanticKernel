import { queryOptions, skipToken, useQuery } from "@tanstack/react-query";
import { fetchConversationMessages } from "../api/conversations";
import { conversationKeys } from "../api/queryKeys";

export function conversationMessagesQueryOptions(conversationId: number) {
  return queryOptions({
    queryKey: conversationKeys.messages(conversationId),
    queryFn: ({ signal }) => fetchConversationMessages(conversationId, { signal }),
  });
}

export function useConversationMessages(conversationId: number | null) {
  return useQuery({
    queryKey: conversationKeys.messages(conversationId ?? 0),
    queryFn:
      conversationId === null
        ? skipToken
        : ({ signal }) => fetchConversationMessages(conversationId, { signal }),
  });
}
