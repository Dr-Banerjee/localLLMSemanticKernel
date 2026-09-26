export type UserRequest = {
  userInput: string;
};

export type ResponseToUserRequest = {
  response: string;
};

export type CurrentUser = {
  id: string;
};

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  kind?: "idiom" | "followup";
};

export type ConversationMessage = {
  id: number;
  role: string;
  content: string;
  createdAt: string;
};

export type ConversationSummary = {
  id: number;
  createdAt: string;
  updatedAt: string;
  initialMessage: string;
};

export type ConversationSummaryResponse = {
  items: ConversationSummary[];
  page: number;
  pageSize: number;
  hasNextPage: boolean;
};

export type ConversationSummariesQueryParams = {
  page: number;
  pageSize: number;
};

export type ParsedExplanation = {
  meaning: string;
  why: string;
  example: string;
  remember: string | null;
};

export type FeaturedIdiom = {
  phrase: string;
  hint: string;
  emoji: string;
  accent: "sky" | "rose" | "violet" | "mint" | "amber" | "peach";
};

export type ChallengeProgress = {
  user_id: string;
  created_at: string;
  updated_at: string;
  challenge_step: number;
};

export type AppScreen = "home" | "summaries" | "conversation" | "challenge";
