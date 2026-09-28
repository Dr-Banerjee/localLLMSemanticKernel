import { useId, useState, type SubmitEvent } from "react";
import { useTranslation } from "react-i18next";
import { challengeIdiomCount } from "../data/challengeIdioms";
import { featuredIdioms } from "../data/featuredIdioms";
import { IdiomCard } from "./IdiomCard";
import { Mascot } from "./Mascot";
import styles from "./HomeScreen.module.css";

type HomeScreenProps = {
  onStart: (idiom: string) => void;
  onViewSummaries: () => void;
  onOpenChallenge: () => void;
};

export function HomeScreen({ onStart, onViewSummaries, onOpenChallenge }: HomeScreenProps) {
  const { t } = useTranslation();
  const inputId = useId();
  const challengeTitleId = useId();
  const [idiom, setIdiom] = useState("");

  function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextIdiom = idiom.trim();
    if (!nextIdiom) {
      return;
    }
    onStart(nextIdiom);
  }

  return (
    <>
      <div className={styles.sun} aria-hidden="true" />
      <div className={`${styles.cloud} ${styles.cloudOne}`} aria-hidden="true" />
      <div className={`${styles.cloud} ${styles.cloudTwo}`} aria-hidden="true" />
      <section className={styles.screen}>
        <header className={styles.hero}>
          <button className={styles.navButton} type="button" onClick={onViewSummaries}>
            {t("home.learned")}
          </button>
          <Mascot mood="cheer" />
          <h1>{t("home.title")}</h1>
          <p className={styles.lead}>{t("home.lead")}</p>
        </header>

        <section className={styles.challenge} aria-labelledby={challengeTitleId}>
          <div className={styles.challengeArt} aria-hidden="true">
            <Mascot mood="happy" className={styles.challengePip} />
            <span className={`${styles.miniStone} ${styles.miniStoneCurrent}`}>1</span>
            <span className={styles.miniPath} />
            <span className={styles.miniStone}>2</span>
            <span className={styles.miniPath} />
            <span className={styles.miniTree} />
            <span className={styles.miniPath} />
            <span className={styles.miniHouse} />
          </div>
          <div className={styles.challengeCopy}>
            <p className={styles.challengeKicker}>
              {t("home.kicker", { count: challengeIdiomCount })}
            </p>
            <h2 id={challengeTitleId}>{t("home.challengeTitle")}</h2>
            <p>{t("home.challengeBody")}</p>
            <button className={styles.challengeCta} type="button" onClick={onOpenChallenge}>
              {t("home.startChallenge")}
            </button>
          </div>
        </section>

        <form className={styles.search} onSubmit={handleSubmit}>
          <label className={styles.srOnly} htmlFor={inputId}>
            {t("home.idiomLabel")}
          </label>
          <input
            id={inputId}
            className={styles.input}
            value={idiom}
            placeholder={t("home.placeholder")}
            autoComplete="off"
            maxLength={500}
            onChange={(event) => setIdiom(event.target.value)}
          />
          <button className={styles.cta} type="submit" disabled={idiom.trim().length === 0}>
            {t("home.askPip")}
          </button>
        </form>

        <div className={styles.picker}>
          <h2>{t("home.pickerTitle")}</h2>
          <div className={styles.grid}>
            {featuredIdioms.map((featuredIdiom) => (
              <IdiomCard key={featuredIdiom.phrase} idiom={featuredIdiom} onSelect={onStart} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
