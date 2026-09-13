import { useEffect, useRef } from "react";
import { followUpPrompts } from "../data/featuredIdioms";
import type { ChatMessage } from "../types";
import { parseExplanation } from "../utils/chat";
import { ChatBubble } from "./ChatBubble";
import { Composer } from "./Composer";
import { ExplanationCard } from "./ExplanationCard";
import { FollowUpChips } from "./FollowUpChips";
import { Mascot } from "./Mascot";
import styles from "./ConversationScreen.module.css";

type ConversationScreenProps = {
  idiom: string;
  messages: ChatMessage[];
  isSending: boolean;
  error: string | null;
  onAsk: (question: string) => void;
  onRetry: () => void;
  onNewIdiom: () => void;
};

function encouragementFor(followUpCount: number): string {
  if (followUpCount >= 5) {
    return "Wow! You are a super idiom explorer.";
  }
  if (followUpCount >= 3) {
    return "Beautiful curiosity. Your brain is growing!";
  }
  if (followUpCount >= 1) {
    return "Great question! Keep exploring.";
  }
  return "Curious questions help you remember.";
}

export function ConversationScreen({
  idiom,
  messages,
  isSending,
  error,
  onAsk,
  onRetry,
  onNewIdiom,
}: ConversationScreenProps) {
  const endRef = useRef<HTMLDivElement>(null);
  const followUpCount = messages.filter((message) => message.kind === "followup").length;
  const firstAssistantId = messages.find((message) => message.role === "assistant")?.id;
  const hasAssistantReply = Boolean(firstAssistantId);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isSending, error]);

  return (
    <section className={styles.screen}>
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <Mascot mood={isSending ? "think" : "happy"} className={styles.mascot} />
          <div>
            <p className={styles.kicker}>Learning with Pip</p>
            <h1 className={styles.idiom}>{idiom}</h1>
          </div>
        </div>
        <button className={styles.newSaying} type="button" onClick={onNewIdiom}>
          New saying
        </button>
      </header>

      <p className={styles.stars} aria-live="polite">
        <span aria-hidden="true">⭐</span>
        {encouragementFor(followUpCount)}
        {followUpCount > 0 ? ` Curious questions: ${followUpCount}` : ""}
      </p>

      <div className={styles.thread} role="log" aria-live="polite" aria-relevant="additions">
        {messages.map((message) => {
          if (message.role === "user") {
            const label =
              message.kind === "idiom" ? `What does “${message.content}” mean?` : message.content;
            return <ChatBubble key={message.id} role="user">{label}</ChatBubble>;
          }

          const explanation =
            message.id === firstAssistantId ? parseExplanation(message.content) : null;
          if (explanation) {
            return <ExplanationCard key={message.id} explanation={explanation} />;
          }

          return (
            <ChatBubble key={message.id} role="assistant">
              {message.content}
            </ChatBubble>
          );
        })}

        {isSending ? (
          <div className={styles.thinking} aria-label="Pip is thinking">
            <span />
            <span />
            <span />
            <p>Pip is thinking of a kind, simple answer...</p>
          </div>
        ) : null}

        {error ? (
          <div className={styles.error} role="alert">
            <p>{error}</p>
            <button type="button" onClick={onRetry}>
              Try again
            </button>
          </div>
        ) : null}

        {!isSending && hasAssistantReply ? (
          <FollowUpChips prompts={followUpPrompts} disabled={isSending} onSelect={onAsk} />
        ) : null}

        <div ref={endRef} />
      </div>

      <div className={styles.composerWrap}>
        <Composer
          placeholder="Ask Pip another question..."
          submitLabel="Ask"
          disabled={isSending}
          onSubmit={onAsk}
        />
      </div>
    </section>
  );
}
