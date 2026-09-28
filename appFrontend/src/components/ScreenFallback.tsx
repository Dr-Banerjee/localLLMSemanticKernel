import { useTranslation } from "react-i18next";
import { Mascot } from "./Mascot";
import styles from "./ScreenFallback.module.css";

export function ScreenFallback() {
  const { t } = useTranslation();

  return (
    <div className={styles.fallback} role="status">
      <Mascot mood="think" />
      <p>{t("fallback.loading")}</p>
    </div>
  );
}
