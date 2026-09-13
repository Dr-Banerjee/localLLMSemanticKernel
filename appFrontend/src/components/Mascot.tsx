import styles from "./Mascot.module.css";

type MascotMood = "happy" | "think" | "cheer";

type MascotProps = {
  mood?: MascotMood;
  className?: string;
};

export function Mascot({ mood = "happy", className }: MascotProps) {
  return (
    <div className={`${styles.wrap} ${styles[mood]} ${className ?? ""}`.trim()} aria-hidden="true">
      <svg className={styles.owl} viewBox="0 0 200 220" role="presentation">
        <ellipse className={styles.shadow} cx="100" cy="208" rx="48" ry="8" />
        <path d="M48 48c0-22 16-38 34-38 10 0 16 6 18 12 2-6 8-12 18-12 18 0 34 16 34 38" fill="#5a331f" />
        <ellipse cx="100" cy="118" rx="72" ry="78" fill="#6b3f2a" />
        <ellipse cx="100" cy="128" rx="52" ry="56" fill="#f4d7a8" />
        <path d="M38 118c-18 8-28 28-22 46 12-10 26-18 42-22z" fill="#5a331f" />
        <path d="M162 118c18 8 28 28 22 46-12-10-26-18-42-22z" fill="#5a331f" />
        <circle cx="72" cy="108" r="28" fill="#fffdf6" />
        <circle cx="128" cy="108" r="28" fill="#fffdf6" />
        <g className={styles.pupils}>
          <circle cx="76" cy="112" r="10" fill="#3a2a1a" />
          <circle cx="132" cy="112" r="10" fill="#3a2a1a" />
          <circle cx="80" cy="108" r="3.5" fill="#fffdf6" />
          <circle cx="136" cy="108" r="3.5" fill="#fffdf6" />
        </g>
        <path d="M100 118l16 22H84z" fill="#f6c453" />
        <path d="M70 178c10 14 50 14 60 0" fill="none" stroke="#3a2a1a" strokeWidth="4" strokeLinecap="round" />
        <path d="M78 196l-10 12M88 198l-4 12M112 198l4 12M122 196l10 12" stroke="#e05a6f" strokeWidth="5" strokeLinecap="round" />
        <circle className={styles.star} cx="164" cy="46" r="8" fill="#ffd45a" />
      </svg>
    </div>
  );
}
