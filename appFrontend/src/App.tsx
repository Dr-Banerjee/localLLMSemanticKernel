import { lazy, Suspense, useCallback, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { messageForApiError } from "./api/errors";
import { fetchVisitedChallengeNode } from "./api/challenge";
import { challengeKeys } from "./api/queryKeys";
import { ScreenFallback } from "./components/ScreenFallback";
import { nextChallengeTarget, readClearedCheckpoint, type ChallengeIdiom } from "./data/challengeIdioms";
import { useInitialiseSession } from "./hooks/useInitialiseSession";
import { conversationMessagesQueryOptions } from "./hooks/useConversationMessages";
import { useAdvanceChallengeStep } from "./hooks/useChallengeProgress";
import { useSendConversationMessage } from "./hooks/useSendConversationMessage";
import { useStartChallengeNode } from "./hooks/useStartChallengeNode";
import type { AppScreen, ChallengeProgress, ChatMessage, ConversationSummary } from "./types";
import {
  createConversationId,
  createMessageId,
  idiomFromMessages,
  mapConversationMessages,
} from "./utils/chat";
import styles from "./App.module.css";

const HomeScreen = lazy(async () => {
  const module = await import("./components/HomeScreen");
  return { default: module.HomeScreen };
});

const ConversationScreen = lazy(async () => {
  const module = await import("./components/ConversationScreen");
  return { default: module.ConversationScreen };
});

const ChallengeConversationScreen = lazy(async () => {
  const module = await import("./components/ChallengeConversationScreen");
  return { default: module.ChallengeConversationScreen };
});

const ConversationSummariesScreen = lazy(async () => {
  const module = await import("./components/ConversationSummariesScreen");
  return { default: module.ConversationSummariesScreen };
});

const ChallengePathScreen = lazy(async () => {
  const module = await import("./components/ChallengePathScreen");
  return { default: module.ChallengePathScreen };
});

function lastUserContent(messages: ChatMessage[]): string | null {
  return messages.findLast((message) => message.role === "user")?.content ?? null;
}

export default function App() {
  const queryClient = useQueryClient();
  const sendMessage = useSendConversationMessage();
  const startChallengeNodeMutation = useStartChallengeNode();
  const advanceStep = useAdvanceChallengeStep();
  useInitialiseSession();

  const [screen, setScreen] = useState<AppScreen>("home");
  const [challengeStoneId, setChallengeStoneId] = useState<number | null>(null);
  const [requestedQuiz, setRequestedQuiz] = useState<number | null>(null);
  const clearRequestedQuiz = useCallback(() => {
    setRequestedQuiz(null);
  }, []);
  const [idiom, setIdiom] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorKind, setErrorKind] = useState<"send" | "load" | null>(null);
  const requestTokenRef = useRef(0);
  const openedSummaryRef = useRef<ConversationSummary | null>(null);

  async function askPip(nextConversationId: number, userInput: string) {
    const token = requestTokenRef.current + 1;
    requestTokenRef.current = token;
    setIsSending(true);
    setError(null);
    setErrorKind(null);

    try {
      const { response } = await sendMessage.mutateAsync({
        conversationId: nextConversationId,
        userInput,
      });
      if (token !== requestTokenRef.current) {
        return;
      }
      const assistantMessage: ChatMessage = {
        id: createMessageId(),
        role: "assistant",
        content: response,
      };
      setMessages((current) => [...current, assistantMessage]);
    } catch (caught) {
      if (token !== requestTokenRef.current) {
        return;
      }
      setError(messageForApiError(caught));
      setErrorKind("send");
    } finally {
      if (token === requestTokenRef.current) {
        setIsSending(false);
      }
    }
  }

  function startConversation(nextIdiom: string) {
    const trimmed = nextIdiom.trim();
    if (!trimmed || isSending) {
      return;
    }

    const nextConversationId = createConversationId();
    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmed,
      kind: "idiom",
    };

    openedSummaryRef.current = null;
    setChallengeStoneId(null);
    setConversationId(nextConversationId);
    setIdiom(trimmed);
    setMessages([userMessage]);
    setIsLoadingHistory(false);
    setError(null);
    setErrorKind(null);
    setScreen("conversation");
    void askPip(nextConversationId, trimmed);
  }

  function askFollowUp(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isSending || isLoadingHistory || conversationId === null) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmed,
      kind: "followup",
    };
    setMessages((current) => [...current, userMessage]);
    void askPip(conversationId, trimmed);
  }

  async function openExistingConversation(summary: ConversationSummary) {
    const token = requestTokenRef.current + 1;
    requestTokenRef.current = token;
    openedSummaryRef.current = summary;
    setChallengeStoneId(null);
    setIsSending(false);
    setConversationId(summary.id);
    setIdiom(summary.initialMessage);
    setMessages([]);
    setError(null);
    setErrorKind(null);
    setIsLoadingHistory(true);
    setScreen("conversation");

    try {
      const history = await queryClient.query(conversationMessagesQueryOptions(summary.id));
      if (token !== requestTokenRef.current) {
        return;
      }
      const mapped = mapConversationMessages(history);
      setMessages(mapped);
      setIdiom(idiomFromMessages(mapped, summary.initialMessage));
    } catch (caught) {
      if (token !== requestTokenRef.current) {
        return;
      }
      setError(messageForApiError(caught));
      setErrorKind("load");
    } finally {
      if (token === requestTokenRef.current) {
        setIsLoadingHistory(false);
      }
    }
  }

  function retryLast() {
    if (errorKind === "load" && openedSummaryRef.current) {
      void openExistingConversation(openedSummaryRef.current);
      return;
    }

    const lastQuestion = lastUserContent(messages);
    if (!lastQuestion || conversationId === null || isSending) {
      return;
    }
    void askPip(conversationId, lastQuestion);
  }

  function resetToHome() {
    requestTokenRef.current += 1;
    openedSummaryRef.current = null;
    setIsSending(false);
    setIsLoadingHistory(false);
    setChallengeStoneId(null);
    setScreen("home");
    setIdiom("");
    setConversationId(null);
    setMessages([]);
    setError(null);
    setErrorKind(null);
  }

  function goToSummaries() {
    requestTokenRef.current += 1;
    setIsSending(false);
    setIsLoadingHistory(false);
    setError(null);
    setErrorKind(null);
    setScreen("summaries");
  }

  function goToChallenge() {
    requestTokenRef.current += 1;
    setIsSending(false);
    setIsLoadingHistory(false);
    setError(null);
    setErrorKind(null);
    setChallengeStoneId(null);
    setScreen("challenge");
  }

  async function openVisitedChallengeNode(entry: ChallengeIdiom) {
    const token = requestTokenRef.current + 1;
    requestTokenRef.current = token;
    const visited = await fetchVisitedChallengeNode(entry.id, (nodeId) =>
      startChallengeNodeMutation.mutateAsync(nodeId),
    );
    if (token !== requestTokenRef.current) {
      return;
    }

    const mapped = mapConversationMessages(visited.messages);
    openedSummaryRef.current = {
      id: visited.conversationId,
      createdAt: "",
      updatedAt: "",
      initialMessage: entry.idiom,
    };
    setIsSending(false);
    setIsLoadingHistory(false);
    setConversationId(visited.conversationId);
    setIdiom(idiomFromMessages(mapped, entry.idiom));
    setMessages(mapped);
    setError(null);
    setErrorKind(null);
    setChallengeStoneId(entry.id);
    setScreen("conversation");
  }

  async function goToNextChallengeStone() {
    if (challengeStoneId === null) {
      return;
    }
    const progress = queryClient.getQueryData<ChallengeProgress>(challengeKeys.progress);
    const clearedThrough = progress ? readClearedCheckpoint(progress.user_id) : 0;
    const next = nextChallengeTarget(challengeStoneId, clearedThrough);
    if (!next) {
      return;
    }
    if (next.kind === "quiz") {
      setRequestedQuiz(next.checkpointId);
      setScreen("challenge");
      return;
    }

    if (progress && progress.challenge_step === next.idiom.id) {
      await advanceStep.mutateAsync(next.idiom.id + 1);
    }
    await openVisitedChallengeNode(next.idiom);
  }

  return (
    <div className={styles.shell}>
      <Suspense fallback={<ScreenFallback />}>
        {screen === "home" ? (
          <HomeScreen
            onStart={startConversation}
            onViewSummaries={goToSummaries}
            onOpenChallenge={goToChallenge}
          />
        ) : null}
        {screen === "summaries" ? (
          <ConversationSummariesScreen
            onBackHome={resetToHome}
            onOpenChallenge={goToChallenge}
            onOpenConversation={(summary) => {
              void openExistingConversation(summary);
            }}
          />
        ) : null}
        {screen === "challenge" ? (
          <ChallengePathScreen
            onBackHome={resetToHome}
            onOpenIdiom={openVisitedChallengeNode}
            openCheckpointQuiz={requestedQuiz}
            onCheckpointQuizOpened={clearRequestedQuiz}
          />
        ) : null}
        {screen === "conversation" && challengeStoneId !== null ? (
          <ChallengeConversationScreen
            stoneId={challengeStoneId}
            idiom={idiom}
            messages={messages}
            isSending={isSending}
            isLoadingHistory={isLoadingHistory}
            error={error}
            onAsk={askFollowUp}
            onRetry={retryLast}
            onNewIdiom={resetToHome}
            onViewSummaries={goToSummaries}
            onOpenChallenge={goToChallenge}
            onNextStone={goToNextChallengeStone}
          />
        ) : null}
        {screen === "conversation" && challengeStoneId === null ? (
          <ConversationScreen
            idiom={idiom}
            messages={messages}
            isSending={isSending}
            isLoadingHistory={isLoadingHistory}
            error={error}
            onAsk={askFollowUp}
            onRetry={retryLast}
            onNewIdiom={resetToHome}
            onViewSummaries={goToSummaries}
            onOpenChallenge={goToChallenge}
          />
        ) : null}
      </Suspense>
    </div>
  );
}
