import styles from "./FollowUpChips.module.css";

type FollowUpChipsProps = {
  prompts: string[];
  disabled?: boolean;
  onSelect: (prompt: string) => void;
};

export function FollowUpChips({ prompts, disabled = false, onSelect }: FollowUpChipsProps) {
  return (
    <section className={styles.wrap} aria-label="Curious follow-up ideas">
      <p className={styles.title}>Still curious? Tap a question!</p>
      <div className={styles.chips}>
        {prompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className={styles.chip}
            disabled={disabled}
            onClick={() => onSelect(prompt)}
          >
            {prompt}
          </button>
        ))}
      </div>
    </section>
  );
}
