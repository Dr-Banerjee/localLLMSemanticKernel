import type { ChatMessage, ChatRole, ConversationMessage, ParsedExplanation } from "../types";

function sliceBetween(text: string, start: RegExp, end: RegExp): string | null {
  const startMatch = start.exec(text);
  if (!startMatch) {
    return null;
  }

  const from = startMatch.index + startMatch[0].length;
  const rest = text.slice(from);
  const endMatch = end.exec(rest);
  const value = (endMatch ? rest.slice(0, endMatch.index) : rest).trim();
  return value.length > 0 ? value : null;
}

export function parseExplanation(text: string): ParsedExplanation | null {
  const normalized = text.replaceAll("\r\n", "\n").trim();
  const meaning = sliceBetween(normalized, /Meaning:/i, /Why does it mean that\??/i);
  const why = sliceBetween(normalized, /Why does it mean that\??/i, /Example:/i);
  const example = sliceBetween(normalized, /Example:/i, /Remember:/i);
  const remember = sliceBetween(normalized, /Remember:/i, /$/i);

  if (!meaning || !why || !example) {
    return null;
  }

  return {
    meaning,
    why,
    example,
    remember,
  };
}

export function createMessageId(): string {
  return crypto.randomUUID();
}

export function createConversationId(): number {
  return Date.now();
}

function isChatRole(role: string): role is ChatRole {
  return role === "user" || role === "assistant";
}

export function mapConversationMessages(messages: ConversationMessage[]): ChatMessage[] {
  const visible = messages.filter((message): message is ConversationMessage & { role: ChatRole } =>
    isChatRole(message.role),
  );
  let seenIdiom = false;

  return visible.map((message) => {
    const chatMessage: ChatMessage = {
      id: String(message.id),
      role: message.role,
      content: message.content,
    };

    if (message.role === "user") {
      chatMessage.kind = seenIdiom ? "followup" : "idiom";
      seenIdiom = true;
    }

    return chatMessage;
  });
}

export function idiomFromMessages(messages: ChatMessage[], fallback: string): string {
  const firstUser = messages.find((message) => message.role === "user");
  return firstUser?.content ?? fallback;
}
