import { infiniteQueryOptions, useInfiniteQuery } from "@tanstack/react-query";
import { DEFAULT_PAGE_SIZE, fetchConversationSummaries } from "../api/conversations";
import { conversationKeys } from "../api/queryKeys";

type UseConversationSummariesOptions = {
  enabled?: boolean;
};

export function conversationSummariesQueryOptions() {
  return infiniteQueryOptions({
    queryKey: conversationKeys.summaries(),
    queryFn: ({ pageParam }) =>
      fetchConversationSummaries({
        page: pageParam,
        pageSize: DEFAULT_PAGE_SIZE,
      }),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => (lastPage.hasNextPage ? lastPage.page + 1 : undefined),
  });
}

export function useConversationSummaries(options: UseConversationSummariesOptions = {}) {
  return useInfiniteQuery({
    ...conversationSummariesQueryOptions(),
    enabled: options.enabled ?? true,
  });
}
