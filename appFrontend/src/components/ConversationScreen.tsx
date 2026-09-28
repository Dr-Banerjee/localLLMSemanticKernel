import { useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { followUpPromptKeys } from "../data/featuredIdioms";
import type { ChatMessage } from "../types";
import { parseExplanation } from "../utils/chat";
import { ChallengeNavButton } from "./ChallengeNavButton";
import { ChatBubble } from "./ChatBubble";
import { Composer } from "./Composer";
import { ExplanationCard } from "./ExplanationCard";
import { FollowUpChips } from "./FollowUpChips";
import { Mascot } from "./Mascot";
import styles from "./ConversationScreen.module.css";

type NextStoneAction = {
  disabled: boolean;
  onNext: () => void;
};

type ConversationScreenProps = {
  idiom: string;
  messages: ChatMessage[];
  isSending: boolean;
  isLoadingHistory?: boolean;
  error: string | null;
  onAsk: (question: string) => void;
  onRetry: () => void;
  onNewIdiom: () => void;
  onViewSummaries: () => void;
  onOpenChallenge: () => void;
  nextStone?: NextStoneAction;
};

function encouragementKey(followUpCount: number): string {
  if (followUpCount >= 5) {
    return "conversation.encouragement5";
  }
  if (followUpCount >= 3) {
    return "conversation.encouragement3";
  }
  if (followUpCount >= 1) {
    return "conversation.encouragement1";
  }
  return "conversation.encouragement0";
}

export function ConversationScreen({
  idiom,
  messages,
  isSending,
  isLoadingHistory = false,
  error,
  onAsk,
  onRetry,
  onNewIdiom,
  onViewSummaries,
  onOpenChallenge,
  nextStone,
}: ConversationScreenProps) {
  const { t } = useTranslation();
  const endRef = useRef<HTMLDivElement>(null);
  const followUpPrompts = followUpPromptKeys.map((key) => t(key));
  const followUpCount = messages.filter((message) => message.kind === "followup").length;
  const firstAssistantId = messages.find((message) => message.role === "assistant")?.id;
  const hasAssistantReply = Boolean(firstAssistantId);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isSending, isLoadingHistory, error]);

  return (
    <section className={styles.screen}>
      <header className={styles.topbar}>
        <div className={styles.brand}>
          <Mascot mood={isSending ? "think" : "happy"} className={styles.mascot} />
          <div>
            <p className={styles.kicker}>{t("conversation.kicker")}</p>
            <h1 className={styles.idiom}>{idiom}</h1>
          </div>
        </div>
        <div className={styles.actions}>
          <ChallengeNavButton onClick={onOpenChallenge} />
          <button className={styles.newSaying} type="button" onClick={onViewSummaries}>
            {t("conversation.yourIdioms")}
          </button>
          <button className={styles.newSaying} type="button" onClick={onNewIdiom}>
            {t("conversation.home")}
          </button>
        </div>
      </header>

      <p className={styles.stars} aria-live="polite">
        <span aria-hidden="true">⭐</span>
        {t(encouragementKey(followUpCount))}
        {followUpCount > 0 ? ` ${t("conversation.curiousCount", { count: followUpCount })}` : ""}
      </p>

      <div className={styles.thread} role="log" aria-live="polite" aria-relevant="additions">
        {messages.map((message) => {
          if (message.role === "user") {
            const label =
              message.kind === "idiom"
                ? t("conversation.userIdiom", { idiom: message.content })
                : message.content;
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

        {isSending || isLoadingHistory ? (
          <div className={styles.thinking} aria-label={t("conversation.thinking")}>
            <span />
            <span />
            <span />
            <p>
              {isLoadingHistory ? t("conversation.opening") : t("conversation.answering")}
            </p>
          </div>
        ) : null}

        {error ? (
          <div className={styles.error} role="alert">
            <p>{error}</p>
            <button type="button" onClick={onRetry}>
              {t("conversation.tryAgain")}
            </button>
          </div>
        ) : null}

        {!isSending && !isLoadingHistory && hasAssistantReply ? (
          <FollowUpChips prompts={followUpPrompts} disabled={isSending} onSelect={onAsk} />
        ) : null}

        <div ref={endRef} />
      </div>

      <div className={styles.composerWrap}>
        <div className={styles.composer}>
          <Composer
            placeholder={t("conversation.placeholder")}
            submitLabel={t("conversation.ask")}
            disabled={isSending || isLoadingHistory}
            onSubmit={onAsk}
          />
        </div>
        {nextStone ? (
          <button
            className={styles.nextStone}
            type="button"
            disabled={nextStone.disabled}
            onClick={nextStone.onNext}
          >
            {t("conversation.nextStone")}
          </button>
        ) : null}
      </div>
    </section>
  );
}
