import { Mascot } from "./Mascot";
import styles from "./ScreenFallback.module.css";

export function ScreenFallback() {
  return (
    <div className={styles.fallback} role="status">
      <Mascot mood="think" />
      <p>Pip is getting the next page ready...</p>
    </div>
  );
}
