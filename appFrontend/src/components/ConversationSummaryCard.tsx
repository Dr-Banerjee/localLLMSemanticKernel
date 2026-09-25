import type { ConversationSummary, FeaturedIdiom } from "../types";
import { formatFriendlyDate } from "../utils/dates";
import styles from "./ConversationSummaryCard.module.css";

const accents: FeaturedIdiom["accent"][] = ["sky", "rose", "violet", "mint", "amber", "peach"];

type ConversationSummaryCardProps = {
  summary: ConversationSummary;
  index: number;
  onOpen: (summary: ConversationSummary) => void;
  onDelete: (summary: ConversationSummary) => void;
  isDeleting?: boolean;
  onPrefetch?: (conversationId: number) => void;
};

export function ConversationSummaryCard({
  summary,
  index,
  onOpen,
  onDelete,
  isDeleting = false,
  onPrefetch,
}: ConversationSummaryCardProps) {
  const accent = accents[index % accents.length];
  const updatedLabel = formatFriendlyDate(summary.updatedAt);

  return (
    <article className={`${styles.card} ${styles[accent]}`}>
      <p className={styles.kicker}>Let’s keep exploring</p>
      <button
        type="button"
        className={styles.idiom}
        onClick={() => onOpen(summary)}
        onFocus={() => onPrefetch?.(summary.id)}
        onMouseEnter={() => onPrefetch?.(summary.id)}
      >
        {summary.initialMessage}
      </button>
      {updatedLabel ? <p className={styles.meta}>Last visited {updatedLabel}</p> : null}
      <p className={styles.hint}>Tap the saying to ask more questions!</p>
      <button
        type="button"
        className={styles.delete}
        aria-label={`Delete ${summary.initialMessage}`}
        disabled={isDeleting}
        onClick={() => onDelete(summary)}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M9 3.5h6M4.5 6.5h15M8 6.5l.7 13h6.6l.7-13"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M10 10.5v6M14 10.5v6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
          />
        </svg>
      </button>
    </article>
  );
}
