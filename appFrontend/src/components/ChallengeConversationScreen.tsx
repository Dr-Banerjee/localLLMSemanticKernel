import { useState } from "react";
import { nextChallengeTarget, readClearedCheckpoint } from "../data/challengeIdioms";
import { useChallengeProgress } from "../hooks/useChallengeProgress";
import { ConversationScreen } from "./ConversationScreen";

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
    <ConversationScreen
      {...conversation}
      isSending={isSending}
      isLoadingHistory={isLoadingHistory}
      nextStone={{
        disabled: !nextTarget || busy,
        onNext: () => {
          void goNext();
        },
      }}
    />
  );
}
