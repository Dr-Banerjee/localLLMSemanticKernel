import { useId, useState, type SubmitEvent } from "react";
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
            Idioms you’ve learned
          </button>
          <Mascot mood="cheer" />
          <p className={styles.kicker}>Pip’s Idiom Nest</p>
          <h1>Come learn idioms with Pip!</h1>
          <p className={styles.lead}>
            An idiom is a playful phrase that means something special, not exactly what the words
            say. Hop the idiom challenge together, or ask about a funny idiom you heard. Curious
            questions help your brain grow!
          </p>
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
            <p className={styles.challengeKicker}>270 idioms · trees · birdhouses</p>
            <h2 id={challengeTitleId}>Help Pip hop the idiom path</h2>
            <p>
              Each stone teaches one new idiom. Every few hops Pip finds a little tree, and every
              ninth stone a brighter birdhouse.
            </p>
            <button className={styles.challengeCta} type="button" onClick={onOpenChallenge}>
              Start Pip's idiom Challenge
            </button>
          </div>
        </section>

        <form className={styles.search} onSubmit={handleSubmit}>
          <label className={styles.srOnly} htmlFor={inputId}>
            Type an idiom
          </label>
          <input
            id={inputId}
            className={styles.input}
            value={idiom}
            placeholder='Try “piece of cake” or “break the ice”'
            autoComplete="off"
            onChange={(event) => setIdiom(event.target.value)}
          />
          <button className={styles.cta} type="submit" disabled={idiom.trim().length === 0}>
            Ask Pip
          </button>
        </form>

        <div className={styles.picker}>
          <h2>Or ask about an idiom you found</h2>
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
