import { useTranslation } from "react-i18next";
import type { AppLanguage } from "../i18n";
import styles from "./LanguageSwitcher.module.css";

const languages = [
  { id: "en", shortLabel: "EN", nameKey: "language.english" },
  { id: "de", shortLabel: "DE", nameKey: "language.german" },
] as const satisfies ReadonlyArray<{ id: AppLanguage; shortLabel: string; nameKey: string }>;

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  const active: AppLanguage = i18n.resolvedLanguage?.startsWith("de") ? "de" : "en";

  return (
    <div className={styles.switcher} role="group" aria-label={t("language.label")}>
      {languages.map((language) => (
        <button
          key={language.id}
          type="button"
          aria-label={t(language.nameKey)}
          aria-pressed={active === language.id}
          onClick={() => {
            void i18n.changeLanguage(language.id);
          }}
        >
          {language.shortLabel}
        </button>
      ))}
    </div>
  );
}
