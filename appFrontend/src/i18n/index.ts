import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import de from "./locales/de.json";
import en from "./locales/en.json";

export const languageStorageKey = "pip.language";

export type AppLanguage = "en" | "de";

function storedLanguage(): AppLanguage {
  const stored = localStorage.getItem(languageStorageKey);
  return stored === "de" ? "de" : "en";
}

export function appLanguage(): AppLanguage {
  return i18n.resolvedLanguage?.startsWith("de") ? "de" : "en";
}

function applyDocumentLanguage(language: string) {
  const next: AppLanguage = language.startsWith("de") ? "de" : "en";
  localStorage.setItem(languageStorageKey, next);
  document.documentElement.lang = next;
  document.title = i18n.t("document.title");
  document.querySelector('meta[name="description"]')?.setAttribute("content", i18n.t("document.description"));
}

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: en },
    de: { translation: de },
  },
  lng: storedLanguage(),
  fallbackLng: "en",
  interpolation: { escapeValue: false },
  react: { useSuspense: false },
});

i18n.on("languageChanged", applyDocumentLanguage);
applyDocumentLanguage(i18n.language);

export default i18n;
