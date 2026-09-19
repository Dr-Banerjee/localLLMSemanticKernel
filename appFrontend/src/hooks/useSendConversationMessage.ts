import { useMutation, useQueryClient } from "@tanstack/react-query";
import { postConversationMessage } from "../api/conversations";
import { conversationKeys } from "../api/queryKeys";

type SendConversationMessageVariables = {
  conversationId: number;
  userInput: string;
};

export function useSendConversationMessage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ conversationId, userInput }: SendConversationMessageVariables) =>
      postConversationMessage(conversationId, userInput),
    onSuccess: async (_data, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: conversationKeys.summaries() }),
        queryClient.invalidateQueries({
          queryKey: conversationKeys.messages(variables.conversationId),
        }),
      ]);
    },
  });
}
