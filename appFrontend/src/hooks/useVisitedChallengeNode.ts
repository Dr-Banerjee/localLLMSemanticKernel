import { queryOptions, skipToken, useQuery, type QueryClient } from "@tanstack/react-query";
import {
  getVisitedChallengeNode,
  isMissingChallengeConversation,
  type VisitedChallengeNode,
} from "../api/challenge";
import { challengeKeys, conversationKeys } from "../api/queryKeys";

export function visitedChallengeNodeQueryOptions(nodeId: number) {
  return queryOptions({
    queryKey: challengeKeys.visited(nodeId),
    queryFn: ({ signal }) => getVisitedChallengeNode(nodeId, { signal }),
    retry: (failureCount, error) =>
      !isMissingChallengeConversation(error) && failureCount < 3,
  });
}

export function useVisitedChallengeNode(nodeId: number | null) {
  return useQuery(
    nodeId === null
      ? {
          queryKey: challengeKeys.visited(0),
          queryFn: skipToken,
        }
      : visitedChallengeNodeQueryOptions(nodeId),
  );
}

function rememberVisitedMessages(queryClient: QueryClient, visited: VisitedChallengeNode) {
  queryClient.setQueryData(conversationKeys.messages(visited.conversationId), visited.messages);
}

export async function ensureVisitedChallengeNode(
  queryClient: QueryClient,
  startNode: (nodeId: number) => Promise<{ conversation_id: number }>,
  nodeId: number,
) {
  try {
    const visited = await queryClient.query(visitedChallengeNodeQueryOptions(nodeId));
    rememberVisitedMessages(queryClient, visited);
    return visited;
  } catch (error) {
    if (!isMissingChallengeConversation(error)) {
      throw error;
    }
  }

  await startNode(nodeId);
  const visited = await queryClient.query(visitedChallengeNodeQueryOptions(nodeId));
  rememberVisitedMessages(queryClient, visited);
  return visited;
}
