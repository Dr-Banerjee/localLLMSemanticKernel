import { useState } from "react";
import { useTranslation } from "react-i18next";
import {
  checkpointPassScore,
  type ChallengeIdiom,
} from "../data/challengeIdioms";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { Mascot } from "./Mascot";
import styles from "./CheckpointQuiz.module.css";

type QuizOption = {
  text: string;
  correct: boolean;
};

type CheckpointQuizProps = {
  idioms: ChallengeIdiom[];
  houseLabel: string;
  finale?: boolean;
  busy: boolean;
  error: string | null;
  onPass: () => void;
  onFail: () => void;
  onCancel: () => void;
};

function shuffledOptions(idiom: ChallengeIdiom): QuizOption[] {
  const options: QuizOption[] = [
    { text: idiom.correct_sentence, correct: true },
    { text: idiom.wrong_sentence, correct: false },
  ];
  if (Math.random() < 0.5) {
    return [options[1], options[0]];
  }
  return options;
}

export function CheckpointQuiz({
  idioms,
  houseLabel,
  finale = false,
  busy,
  error,
  onPass,
  onFail,
  onCancel,
}: CheckpointQuizProps) {
  const { t } = useTranslation();
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [picked, setPicked] = useState<number | null>(null);
  const [options, setOptions] = useState<QuizOption[]>(() => shuffledOptions(idioms[0]));
  const [finished, setFinished] = useState(false);

  const passed = score >= checkpointPassScore;
  const current = idioms[index];

  function choose(optionIndex: number) {
    if (finished) {
      return;
    }
    setPicked(optionIndex);
  }

  function goNext() {
    if (picked === null) {
      return;
    }
    const nextScore = score + (options[picked].correct ? 1 : 0);
    const nextIndex = index + 1;
    if (nextIndex >= idioms.length) {
      setScore(nextScore);
      setFinished(true);
      return;
    }
    setScore(nextScore);
    setPicked(null);
    setIndex(nextIndex);
    setOptions(shuffledOptions(idioms[nextIndex]));
  }

  return (
    <section className={styles.screen}>
      <header className={styles.header}>
        <div className={styles.corner}>
          <LanguageSwitcher />
          <button className={styles.back} type="button" onClick={onCancel}>
            {t("quiz.backToPath")}
          </button>
        </div>
        <p className={styles.kicker}>{finale ? t("quiz.lastTest") : t("quiz.checkpoint")}</p>
        <h1>{finished ? t("quiz.howDidPip") : houseLabel}</h1>
      </header>

      <Mascot
        mood={finished ? (passed ? "cheer" : "think") : "think"}
        className={styles.pip}
      />

      {finished ? (
        <div className={styles.card}>
          <p className={styles.score}>
            {t("quiz.score", { score, total: idioms.length })}
          </p>
          {passed ? (
            <p>
              {finale
                ? t("quiz.passFinale", { house: houseLabel })
                : t("quiz.pass", { house: houseLabel })}
            </p>
          ) : (
            <p>
              {finale
                ? t("quiz.failFinale", { house: houseLabel })
                : t("quiz.fail", { house: houseLabel })}
            </p>
          )}
          {error ? (
            <p className={styles.error} role="alert">
              {error}
            </p>
          ) : null}
          {passed ? (
            <button type="button" className={styles.primary} disabled={busy} onClick={onPass}>
              {busy
                ? t("quiz.hopping")
                : finale
                  ? t("quiz.reach", { house: houseLabel })
                  : t("quiz.onTo", { house: houseLabel })}
            </button>
          ) : (
            <button type="button" className={styles.primary} onClick={onFail}>
              {t("quiz.backToStones")}
            </button>
          )}
        </div>
      ) : (
        <div className={styles.card}>
          <p className={styles.progress}>
            {t("quiz.question", { current: index + 1, total: idioms.length })}
          </p>
          <h2 className={styles.idiom}>{current.idiom}</h2>
          <p>{t("quiz.whichSentence")}</p>
          <div className={styles.choices} role="group" aria-label={t("quiz.choices", { idiom: current.idiom })}>
            {options.map((option, optionIndex) => {
              const selected = picked === optionIndex;
              return (
                <button
                  key={option.text}
                  type="button"
                  className={`${styles.choice} ${selected ? styles.selected : ""}`}
                  aria-pressed={selected}
                  onClick={() => {
                    choose(optionIndex);
                  }}
                >
                  {option.text}
                </button>
              );
            })}
          </div>
          <button type="button" className={styles.primary} disabled={picked === null} onClick={goNext}>
            {index + 1 === idioms.length ? t("quiz.seeScore") : t("quiz.nextSaying")}
          </button>
        </div>
      )}
    </section>
  );
}
