import { useMemo } from "react";
import { noop, useQueryClient } from "@tanstack/react-query";
import { conversationMessagesQueryOptions } from "../hooks/useConversationMessages";
import { useConversationSummaries } from "../hooks/useConversationSummaries";
import type { ConversationSummary } from "../types";
import { ConversationSummaryCard } from "./ConversationSummaryCard";
import { Mascot } from "./Mascot";
import styles from "./ConversationSummariesScreen.module.css";

type ConversationSummariesScreenProps = {
  onBackHome: () => void;
  onOpenConversation: (summary: ConversationSummary) => void;
};

export function ConversationSummariesScreen({
  onBackHome,
  onOpenConversation,
}: ConversationSummariesScreenProps) {
  const queryClient = useQueryClient();
  const summariesQuery = useConversationSummaries();

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
        <Mascot mood="happy" className={styles.mascot} />
        <p className={styles.kicker}>Your idiom nest</p>
        <h1>Sayings you already started exploring</h1>
        <p className={styles.lead}>
          Pick a favorite and ask another curious question. Pip is happy to keep teaching!
        </p>
        <button className={styles.homeButton} type="button" onClick={onBackHome}>
          Learn a new saying
        </button>
      </header>

      {isLoading ? (
        <div className={styles.grid} aria-busy="true" aria-label="Loading your sayings">
          {Array.from({ length: 6 }, (_, index) => (
            <div key={index} className={styles.skeleton} />
          ))}
        </div>
      ) : null}

      {error ? (
        <div className={styles.banner} role="alert">
          <p>Pip couldn’t find your nest just now. Let’s try again!</p>
          <button
            type="button"
            onClick={() => {
              void summariesQuery.refetch();
            }}
          >
            Try again
          </button>
        </div>
      ) : null}

      {!isLoading && !error && summaries.length === 0 ? (
        <div className={styles.empty}>
          <p>Your nest is waiting for its first saying!</p>
          <p>Learn one with Pip, then it will show up here so you can visit it again.</p>
          <button type="button" onClick={onBackHome}>
            Let’s learn a saying
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
              {summariesQuery.isFetchingNextPage ? "Finding more sayings..." : "More conversations"}
            </button>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
