import type { ParsedExplanation } from "../types";
import styles from "./ExplanationCard.module.css";

type ExplanationCardProps = {
  explanation: ParsedExplanation;
};

const sections = [
  { key: "meaning", title: "What it means", emoji: "💡", field: "meaning" },
  { key: "why", title: "Why people say it", emoji: "🌈", field: "why" },
  { key: "example", title: "A friendly example", emoji: "📖", field: "example" },
  { key: "remember", title: "Remember this", emoji: "⭐", field: "remember" },
] as const;

export function ExplanationCard({ explanation }: ExplanationCardProps) {
  return (
    <article className={styles.stack} aria-label="Idiom explanation">
      {sections.map((section) => {
        const body = explanation[section.field];
        if (!body) {
          return null;
        }

        return (
          <section key={section.key} className={`${styles.card} ${styles[section.key]}`}>
            <h3>
              <span aria-hidden="true">{section.emoji}</span>
              {section.title}
            </h3>
            <p>{body}</p>
          </section>
        );
      })}
    </article>
  );
}
