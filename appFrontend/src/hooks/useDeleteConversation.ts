import {
  type InfiniteData,
  mutationOptions,
  useMutation,
} from "@tanstack/react-query";
import { deleteConversation } from "../api/conversations";
import { conversationKeys } from "../api/queryKeys";
import type { ConversationSummaryResponse } from "../types";

function withoutConversation(
  data: InfiniteData<ConversationSummaryResponse> | undefined,
  conversationId: number,
): InfiniteData<ConversationSummaryResponse> | undefined {
  if (!data) {
    return data;
  }

  return {
    ...data,
    pages: data.pages.map((page) => ({
      ...page,
      items: page.items.filter((item) => item.id !== conversationId),
    })),
  };
}

export function deleteConversationMutationOptions() {
  return mutationOptions({
    mutationFn: (conversationId: number) => deleteConversation(conversationId),
    onMutate: async (conversationId, { client }) => {
      await client.cancelQueries({ queryKey: conversationKeys.summaries() });
      const previousSummaries = client.getQueryData<
        InfiniteData<ConversationSummaryResponse>
      >(conversationKeys.summaries());
      client.setQueryData<InfiniteData<ConversationSummaryResponse>>(
        conversationKeys.summaries(),
        (current) => withoutConversation(current, conversationId),
      );
      return { previousSummaries };
    },
    onError: (_error, _conversationId, onMutateResult, { client }) => {
      if (onMutateResult?.previousSummaries) {
        client.setQueryData(conversationKeys.summaries(), onMutateResult.previousSummaries);
      }
    },
    onSettled: async (_data, _error, conversationId, _onMutateResult, { client }) => {
      await Promise.all([
        client.invalidateQueries({ queryKey: conversationKeys.summaries() }),
        client.invalidateQueries({
          queryKey: conversationKeys.messages(conversationId),
        }),
      ]);
    },
  });
}

export function useDeleteConversation() {
  return useMutation(deleteConversationMutationOptions());
}
