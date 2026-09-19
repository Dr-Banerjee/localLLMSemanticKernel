import { useState, type FormEvent } from "react";
import { featuredIdioms } from "../data/featuredIdioms";
import { IdiomCard } from "./IdiomCard";
import { Mascot } from "./Mascot";
import styles from "./HomeScreen.module.css";

type HomeScreenProps = {
  onStart: (idiom: string) => void;
  onViewSummaries: () => void;
};

export function HomeScreen({ onStart, onViewSummaries }: HomeScreenProps) {
  const [idiom, setIdiom] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextIdiom = idiom.trim();
    if (!nextIdiom) {
      return;
    }
    onStart(nextIdiom);
  }

  return (
    <section className={styles.screen}>
      <div className={styles.sun} aria-hidden="true" />
      <div className={`${styles.cloud} ${styles.cloudOne}`} aria-hidden="true" />
      <div className={`${styles.cloud} ${styles.cloudTwo}`} aria-hidden="true" />

      <header className={styles.hero}>
        <button className={styles.navButton} type="button" onClick={onViewSummaries}>
          Sayings you’ve learned
        </button>
        <Mascot mood="happy" />
        <p className={styles.kicker}>Pip’s Idiom Nest</p>
        <h1>Heard a funny saying? Let’s figure it out together!</h1>
        <p className={styles.lead}>
          Idioms are playful phrases that mean something special. Type one you heard, or pick a
          favorite below. Curious questions help your brain grow!
        </p>
      </header>

      <form className={styles.search} onSubmit={handleSubmit}>
        <label className={styles.srOnly} htmlFor="idiom-input">
          Type an idiom
        </label>
        <input
          id="idiom-input"
          className={styles.input}
          value={idiom}
          placeholder='Try “piece of cake” or “break the ice”'
          autoComplete="off"
          onChange={(event) => setIdiom(event.target.value)}
        />
        <button className={styles.cta} type="submit" disabled={idiom.trim().length === 0}>
          Let’s learn!
        </button>
      </form>

      <div className={styles.picker}>
        <h2>Or tap a fun saying</h2>
        <div className={styles.grid}>
          {featuredIdioms.map((featuredIdiom) => (
            <IdiomCard key={featuredIdiom.phrase} idiom={featuredIdiom} onSelect={onStart} />
          ))}
        </div>
      </div>
    </section>
  );
}
