import { useTranslation } from "react-i18next";
import styles from "./FollowUpChips.module.css";

type FollowUpChipsProps = {
  prompts: string[];
  disabled?: boolean;
  onSelect: (prompt: string) => void;
};

export function FollowUpChips({ prompts, disabled = false, onSelect }: FollowUpChipsProps) {
  const { t } = useTranslation();

  return (
    <section className={styles.wrap} aria-label={t("followUp.label")}>
      <p className={styles.title}>{t("followUp.title")}</p>
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
