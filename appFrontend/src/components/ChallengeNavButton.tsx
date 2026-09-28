import { useTranslation } from "react-i18next";
import styles from "./ChallengeNavButton.module.css";

type ChallengeNavButtonProps = {
  onClick: () => void;
};

export function ChallengeNavButton({ onClick }: ChallengeNavButtonProps) {
  const { t } = useTranslation();

  return (
    <button className={styles.button} type="button" onClick={onClick}>
      {t("nav.challenge")}
    </button>
  );
}
