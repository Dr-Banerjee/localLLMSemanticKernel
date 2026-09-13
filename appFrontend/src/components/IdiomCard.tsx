import type { FeaturedIdiom } from "../types";
import styles from "./IdiomCard.module.css";

type IdiomCardProps = {
  idiom: FeaturedIdiom;
  onSelect: (phrase: string) => void;
};

export function IdiomCard({ idiom, onSelect }: IdiomCardProps) {
  return (
    <button
      type="button"
      className={`${styles.card} ${styles[idiom.accent]}`}
      onClick={() => onSelect(idiom.phrase)}
    >
      <span className={styles.emoji} aria-hidden="true">
        {idiom.emoji}
      </span>
      <span className={styles.phrase}>{idiom.phrase}</span>
      <span className={styles.hint}>{idiom.hint}</span>
    </button>
  );
}
