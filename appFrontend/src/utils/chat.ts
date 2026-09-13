import type { ParsedExplanation } from "../types";

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
  const normalized = text.replace(/\r\n/g, "\n").trim();
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
