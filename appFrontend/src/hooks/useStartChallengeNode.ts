import { mutationOptions, useMutation } from "@tanstack/react-query";
import { startChallengeNode } from "../api/challenge";
import { conversationKeys } from "../api/queryKeys";

export function startChallengeNodeMutationOptions() {
  return mutationOptions({
    mutationFn: (nodeId: number) => startChallengeNode(nodeId),
    onSettled: async (data, _error, _nodeId, _onMutateResult, { client }) => {
      if (!data) {
        return;
      }
      await Promise.all([
        client.invalidateQueries({ queryKey: conversationKeys.summaries() }),
        client.invalidateQueries({
          queryKey: conversationKeys.messages(data.conversation_id),
        }),
      ]);
    },
  });
}

export function useStartChallengeNode() {
  return useMutation(startChallengeNodeMutationOptions());
}
