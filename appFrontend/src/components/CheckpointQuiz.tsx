import { useState } from "react";
import {
  checkpointPassScore,
  type ChallengeIdiom,
} from "../data/challengeIdioms";
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
        <button className={styles.back} type="button" onClick={onCancel}>
          Back to the path
        </button>
        <p className={styles.kicker}>{finale ? "Last test" : "Checkpoint test"}</p>
        <h1>{finished ? "How did Pip do?" : houseLabel}</h1>
      </header>

      <Mascot
        mood={finished ? (passed ? "cheer" : "think") : "think"}
        className={styles.pip}
      />

      {finished ? (
        <div className={styles.card}>
          <p className={styles.score}>
            {score} of {idioms.length} right
          </p>
          {passed ? (
            <p>
              {finale
                ? `Pip knows these sayings well enough to reach ${houseLabel}, the grand birdhouse at the end of the path.`
                : `Pip knows these sayings well enough to hop on to ${houseLabel}.`}
            </p>
          ) : (
            <p>
              {finale
                ? `Pip is not ready for ${houseLabel} yet. That grand birdhouse is the end of the path. Revisit the stones behind you to freshen up, then try the last test again.`
                : `Pip is not ready for ${houseLabel} yet. Revisit the stones behind you to freshen up, then try the test again.`}
            </p>
          )}
          {error ? (
            <p className={styles.error} role="alert">
              {error}
            </p>
          ) : null}
          {passed ? (
            <button type="button" className={styles.primary} disabled={busy} onClick={onPass}>
              {busy ? "Pip is hopping..." : finale ? `Reach ${houseLabel}` : `On to ${houseLabel}`}
            </button>
          ) : (
            <button type="button" className={styles.primary} onClick={onFail}>
              Back to the stones
            </button>
          )}
        </div>
      ) : (
        <div className={styles.card}>
          <p className={styles.progress}>
            Question {index + 1} of {idioms.length}
          </p>
          <h2 className={styles.idiom}>{current.idiom}</h2>
          <p>Which sentence uses this saying the right way?</p>
          <div className={styles.choices} role="group" aria-label={`Choices for ${current.idiom}`}>
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
            {index + 1 === idioms.length ? "See the score" : "Next saying"}
          </button>
        </div>
      )}
    </section>
  );
}
