import styles from "./ChallengeNavButton.module.css";

type ChallengeNavButtonProps = {
  onClick: () => void;
};

export function ChallengeNavButton({ onClick }: ChallengeNavButtonProps) {
  return (
    <button className={styles.button} type="button" onClick={onClick}>
      Pip's idiom Challenge
    </button>
  );
}
