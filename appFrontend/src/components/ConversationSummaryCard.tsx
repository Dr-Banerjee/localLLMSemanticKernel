import type { ConversationSummary, FeaturedIdiom } from "../types";
import { formatFriendlyDate } from "../utils/dates";
import styles from "./ConversationSummaryCard.module.css";

const accents: FeaturedIdiom["accent"][] = ["sky", "rose", "violet", "mint", "amber", "peach"];

type ConversationSummaryCardProps = {
  summary: ConversationSummary;
  index: number;
  onOpen: (summary: ConversationSummary) => void;
  onPrefetch?: (conversationId: number) => void;
};

export function ConversationSummaryCard({
  summary,
  index,
  onOpen,
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
    </article>
  );
}
