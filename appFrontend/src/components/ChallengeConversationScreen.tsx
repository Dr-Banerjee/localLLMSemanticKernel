import { useState } from "react";
import { nextChallengeTarget, readClearedCheckpoint } from "../data/challengeIdioms";
import { useChallengeProgress } from "../hooks/useChallengeProgress";
import { ConversationScreen } from "./ConversationScreen";
import styles from "./ChallengeConversationScreen.module.css";

type ChallengeConversationScreenProps = {
  stoneId: number;
  idiom: string;
  messages: Parameters<typeof ConversationScreen>[0]["messages"];
  isSending: boolean;
  isLoadingHistory?: boolean;
  error: string | null;
  onAsk: (question: string) => void;
  onRetry: () => void;
  onNewIdiom: () => void;
  onViewSummaries: () => void;
  onOpenChallenge: () => void;
  onNextStone: () => Promise<void>;
};

export function ChallengeConversationScreen({
  stoneId,
  onNextStone,
  isSending,
  isLoadingHistory = false,
  ...conversation
}: ChallengeConversationScreenProps) {
  const progressQuery = useChallengeProgress();
  const [isHopping, setIsHopping] = useState(false);
  const progress = progressQuery.data;
  const nextTarget = nextChallengeTarget(
    stoneId,
    progress ? readClearedCheckpoint(progress.user_id) : 0,
  );
  const busy = isSending || isLoadingHistory || isHopping;

  async function goNext() {
    if (!nextTarget || busy) {
      return;
    }
    setIsHopping(true);
    try {
      await onNextStone();
    } finally {
      setIsHopping(false);
    }
  }

  return (
    <div className={styles.frame}>
      <ConversationScreen
        {...conversation}
        isSending={isSending}
        isLoadingHistory={isLoadingHistory}
      />
      <div className={styles.nav}>
        <button
          type="button"
          disabled={!nextTarget || busy}
          onClick={() => {
            void goNext();
          }}
        >
          Next stone
        </button>
      </div>
    </div>
  );
}
