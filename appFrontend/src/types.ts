export type UserRequest = {
  userInput: string;
};

export type ResponseToUserRequest = {
  response: string;
};

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  kind?: "idiom" | "followup";
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
