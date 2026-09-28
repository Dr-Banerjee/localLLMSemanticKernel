import { useTranslation } from "react-i18next";
import type { ParsedExplanation } from "../types";
import styles from "./ExplanationCard.module.css";

type ExplanationCardProps = {
  explanation: ParsedExplanation;
};

const sections = [
  { key: "meaning", titleKey: "explanation.meaning", emoji: "💡", field: "meaning" },
  { key: "why", titleKey: "explanation.why", emoji: "🌈", field: "why" },
  { key: "example", titleKey: "explanation.example", emoji: "📖", field: "example" },
  { key: "remember", titleKey: "explanation.remember", emoji: "⭐", field: "remember" },
] as const;

export function ExplanationCard({ explanation }: ExplanationCardProps) {
  const { t } = useTranslation();

  return (
    <article className={styles.stack} aria-label={t("explanation.label")}>
      {sections.map((section) => {
        const body = explanation[section.field];
        if (!body) {
          return null;
        }

        return (
          <section key={section.key} className={`${styles.card} ${styles[section.key]}`}>
            <h3>
              <span aria-hidden="true">{section.emoji}</span>
              {t(section.titleKey)}
            </h3>
            <p>{body}</p>
          </section>
        );
      })}
    </article>
  );
}
