import styles from "./ChatBubble.module.css";

type ChatBubbleProps = {
  role: "user" | "assistant";
  children: string;
};

export function ChatBubble({ role, children }: ChatBubbleProps) {
  return (
    <div className={`${styles.row} ${styles[role]}`}>
      <p className={styles.bubble}>{children}</p>
    </div>
  );
}
