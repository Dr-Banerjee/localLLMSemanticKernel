import i18n from "../i18n";

export function formatFriendlyDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const diffMs = Date.now() - date.getTime();
  const minutes = Math.max(0, Math.floor(diffMs / 60_000));

  if (minutes < 1) {
    return i18n.t("dates.justNow");
  }
  if (minutes < 60) {
    return i18n.t("dates.minutesAgo", { count: minutes });
  }

  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return i18n.t("dates.hoursAgo", { count: hours });
  }

  const days = Math.floor(hours / 24);
  if (days === 1) {
    return i18n.t("dates.yesterday");
  }
  if (days < 7) {
    return i18n.t("dates.daysAgo", { count: days });
  }

  const language = i18n.resolvedLanguage?.startsWith("de") ? "de" : "en";
  return date.toLocaleDateString(language, {
    month: "short",
    day: "numeric",
  });
}
