export const conversationKeys = {
  all: ["conversations"] as const,
  summaries: () => [...conversationKeys.all, "summaries"] as const,
  messages: (conversationId: number) =>
    [...conversationKeys.all, conversationId, "messages"] as const,
};

export const sessionKeys = {
  current: ["session"] as const,
};
