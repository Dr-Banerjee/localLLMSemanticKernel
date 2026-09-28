import { useMemo } from "react";
import { noop, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { conversationMessagesQueryOptions } from "../hooks/useConversationMessages";
import { useConversationSummaries } from "../hooks/useConversationSummaries";
import { useDeleteConversation } from "../hooks/useDeleteConversation";
import type { ConversationSummary } from "../types";
import { ConversationSummaryCard } from "./ConversationSummaryCard";
import { ChallengeNavButton } from "./ChallengeNavButton";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { Mascot } from "./Mascot";
import styles from "./ConversationSummariesScreen.module.css";

type ConversationSummariesScreenProps = {
  onBackHome: () => void;
  onOpenConversation: (summary: ConversationSummary) => void;
  onOpenChallenge: () => void;
};

export function ConversationSummariesScreen({
  onBackHome,
  onOpenConversation,
  onOpenChallenge,
}: ConversationSummariesScreenProps) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const summariesQuery = useConversationSummaries();
  const deleteConversation = useDeleteConversation();

  const summaries = useMemo(
    () => summariesQuery.data?.pages.flatMap((page) => page.items) ?? [],
    [summariesQuery.data],
  );

  function prefetchMessages(conversationId: number) {
    void queryClient.query(conversationMessagesQueryOptions(conversationId)).catch(noop);
  }

  const isLoading = summariesQuery.isPending;
  const error = summariesQuery.error;

  return (
    <section className={styles.screen}>
      <header className={styles.header}>
        <div className={styles.corner}>
          <LanguageSwitcher />
          <Mascot mood="happy" className={styles.mascot} />
        </div>
        <h1>{t("summaries.title")}</h1>
        <p className={styles.lead}>{t("summaries.lead")}</p>
        <div className={styles.headerActions}>
          <ChallengeNavButton onClick={onOpenChallenge} />
          <button className={styles.kicker} type="button" onClick={onBackHome}>
            {t("summaries.home")}
          </button>
        </div>
      </header>

      {isLoading ? (
        <div className={styles.grid} aria-busy="true" aria-label={t("summaries.loading")}>
          {Array.from({ length: 6 }, (_, index) => (
            <div key={index} className={styles.skeleton} />
          ))}
        </div>
      ) : null}

      {error ? (
        <div className={styles.banner} role="alert">
          <p>{t("summaries.error")}</p>
          <button
            type="button"
            onClick={() => {
              void summariesQuery.refetch();
            }}
          >
            {t("summaries.tryAgain")}
          </button>
        </div>
      ) : null}

      {!isLoading && !error && summaries.length === 0 ? (
        <div className={styles.empty}>
          <p>{t("summaries.emptyTitle")}</p>
          <p>{t("summaries.emptyBody")}</p>
          <button type="button" onClick={onBackHome}>
            {t("summaries.emptyCta")}
          </button>
        </div>
      ) : null}

      {!isLoading && !error && summaries.length > 0 ? (
        <>
          <div className={styles.grid}>
            {summaries.map((summary, index) => (
              <ConversationSummaryCard
                key={summary.id}
                summary={summary}
                index={index}
                onOpen={onOpenConversation}
                onDelete={(selected) => {
                  deleteConversation.mutate(selected.id);
                }}
                isDeleting={
                  deleteConversation.isPending && deleteConversation.variables === summary.id
                }
                onPrefetch={prefetchMessages}
              />
            ))}
          </div>
          {summariesQuery.hasNextPage ? (
            <button
              className={styles.more}
              type="button"
              onClick={() => {
                void summariesQuery.fetchNextPage();
              }}
              disabled={summariesQuery.isFetchingNextPage}
            >
              {summariesQuery.isFetchingNextPage ? t("summaries.moreLoading") : t("summaries.more")}
            </button>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
