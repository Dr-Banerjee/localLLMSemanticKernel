import { mutationOptions, useMutation } from "@tanstack/react-query";
import { postConversationMessage } from "../api/conversations";
import { conversationKeys } from "../api/queryKeys";

type SendConversationMessageVariables = {
  conversationId: number;
  userInput: string;
};

export function sendConversationMessageMutationOptions() {
  return mutationOptions({
    mutationFn: ({ conversationId, userInput }: SendConversationMessageVariables) =>
      postConversationMessage(conversationId, userInput),
    onSuccess: async (_data, variables, _onMutateResult, { client }) => {
      await Promise.all([
        client.invalidateQueries({ queryKey: conversationKeys.summaries() }),
        client.invalidateQueries({
          queryKey: conversationKeys.messages(variables.conversationId),
        }),
      ]);
    },
  });
}

export function useSendConversationMessage() {
  return useMutation(sendConversationMessageMutationOptions());
}
