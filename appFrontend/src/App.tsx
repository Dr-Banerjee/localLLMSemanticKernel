import { lazy, Suspense, useCallback, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { messageForApiError } from "./api/errors";
import { challengeKeys } from "./api/queryKeys";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { ScreenFallback } from "./components/ScreenFallback";
import { nextChallengeTarget, readClearedCheckpoint, type ChallengeIdiom } from "./data/challengeIdioms";
import { useInitialiseSession } from "./hooks/useInitialiseSession";
import { useConversationMessages } from "./hooks/useConversationMessages";
import { useAdvanceChallengeStep } from "./hooks/useChallengeProgress";
import { useSendConversationMessage } from "./hooks/useSendConversationMessage";
import { useStartChallengeNode } from "./hooks/useStartChallengeNode";
import { ensureVisitedChallengeNode, useVisitedChallengeNode } from "./hooks/useVisitedChallengeNode";
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

function visibleThread(
  serverMessages: ChatMessage[] | null,
  draftMessages: ChatMessage[] | null,
): ChatMessage[] {
  if (
    serverMessages &&
    (draftMessages === null || serverMessages.length >= draftMessages.length)
  ) {
    return serverMessages;
  }
  return draftMessages ?? [];
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
  const [syncMessages, setSyncMessages] = useState(false);
  const [draftMessages, setDraftMessages] = useState<ChatMessage[] | null>(null);
  const [sendingConversationId, setSendingConversationId] = useState<number | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const navigationRef = useRef(0);
  const activeSendIdRef = useRef<number | null>(null);
  const visitedQuery = useVisitedChallengeNode(challengeStoneId);
  const visitedConversationId = visitedQuery.data?.conversationId ?? null;
  const activeConversationId =
    challengeStoneId !== null ? visitedConversationId : conversationId;
  const messageQueryId =
    challengeStoneId !== null ? visitedConversationId : syncMessages ? conversationId : null;
  const messagesQuery = useConversationMessages(messageQueryId);
  const serverMessages = messagesQuery.data ? mapConversationMessages(messagesQuery.data) : null;
  const messages = visibleThread(serverMessages, draftMessages);
  const displayedIdiom = idiomFromMessages(messages, idiom);
  const showingDraft =
    draftMessages !== null &&
    (serverMessages === null || draftMessages.length > serverMessages.length);
  const isSending =
    sendingConversationId !== null &&
    sendingConversationId === activeConversationId &&
    sendMessage.isPending &&
    showingDraft;
  const isLoadingHistory =
    messages.length === 0 &&
    ((challengeStoneId !== null && visitedQuery.isLoading) || messagesQuery.isLoading);
  const loadError =
    messageQueryId !== null && messagesQuery.isError && !messagesQuery.data
      ? messageForApiError(messagesQuery.error)
      : null;
  const visitedError =
    challengeStoneId !== null && visitedQuery.isError && !visitedQuery.data
      ? messageForApiError(visitedQuery.error)
      : null;
  const error = sendError ?? visitedError ?? loadError;

  function stopOutgoingSend() {
    activeSendIdRef.current = null;
    setSendingConversationId(null);
    setSendError(null);
  }

  async function askPip(nextConversationId: number, userInput: string) {
    activeSendIdRef.current = nextConversationId;
    setSendingConversationId(nextConversationId);
    setSendError(null);

    try {
      const { response } = await sendMessage.mutateAsync({
        conversationId: nextConversationId,
        userInput,
      });
      if (activeSendIdRef.current !== nextConversationId) {
        return;
      }
      setSyncMessages(true);
      setDraftMessages((current) => {
        if (!current) {
          return current;
        }
        const last = current[current.length - 1];
        if (last?.role === "assistant") {
          return current;
        }
        const assistantMessage: ChatMessage = {
          id: createMessageId(),
          role: "assistant",
          content: response,
        };
        return [...current, assistantMessage];
      });
    } catch (caught) {
      if (activeSendIdRef.current !== nextConversationId) {
        return;
      }
      setSendError(messageForApiError(caught));
    } finally {
      if (activeSendIdRef.current === nextConversationId) {
        setSendingConversationId(null);
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

    navigationRef.current += 1;
    stopOutgoingSend();
    setChallengeStoneId(null);
    setSyncMessages(false);
    setConversationId(nextConversationId);
    setIdiom(trimmed);
    setDraftMessages([userMessage]);
    setScreen("conversation");
    void askPip(nextConversationId, trimmed);
  }

  function askFollowUp(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isSending || isLoadingHistory || activeConversationId === null) {
      return;
    }

    const userMessage: ChatMessage = {
      id: createMessageId(),
      role: "user",
      content: trimmed,
      kind: "followup",
    };
    const base =
      serverMessages &&
      (draftMessages === null || serverMessages.length >= draftMessages.length)
        ? serverMessages
        : (draftMessages ?? []);
    setDraftMessages([...base, userMessage]);
    void askPip(activeConversationId, trimmed);
  }

  function openExistingConversation(summary: ConversationSummary) {
    navigationRef.current += 1;
    stopOutgoingSend();
    setChallengeStoneId(null);
    setSyncMessages(true);
    setDraftMessages(null);
    setConversationId(summary.id);
    setIdiom(summary.initialMessage);
    setScreen("conversation");
  }

  function retryLast() {
    if (sendError) {
      const lastQuestion = lastUserContent(messages);
      if (!lastQuestion || activeConversationId === null || isSending) {
        return;
      }
      void askPip(activeConversationId, lastQuestion);
      return;
    }

    if (messageQueryId !== null && messagesQuery.isError) {
      void messagesQuery.refetch();
      return;
    }

    if (challengeStoneId !== null && visitedQuery.isError) {
      void visitedQuery.refetch();
    }
  }

  function resetToHome() {
    navigationRef.current += 1;
    stopOutgoingSend();
    setDraftMessages(null);
    setSyncMessages(false);
    setChallengeStoneId(null);
    setScreen("home");
    setIdiom("");
    setConversationId(null);
  }

  function goToSummaries() {
    navigationRef.current += 1;
    stopOutgoingSend();
    setDraftMessages(null);
    setScreen("summaries");
  }

  function goToChallenge() {
    navigationRef.current += 1;
    stopOutgoingSend();
    setDraftMessages(null);
    setChallengeStoneId(null);
    setScreen("challenge");
  }

  async function openVisitedChallengeNode(entry: ChallengeIdiom) {
    const token = navigationRef.current + 1;
    navigationRef.current = token;
    stopOutgoingSend();
    const visited = await ensureVisitedChallengeNode(
      queryClient,
      (nodeId) => startChallengeNodeMutation.mutateAsync(nodeId),
      entry.id,
    );
    if (token !== navigationRef.current) {
      return;
    }

    setDraftMessages(null);
    setSyncMessages(true);
    setConversationId(null);
    setIdiom(idiomFromMessages(mapConversationMessages(visited.messages), entry.idiom));
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
      navigationRef.current += 1;
      stopOutgoingSend();
      setDraftMessages(null);
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
      <LanguageSwitcher />
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
            idiom={displayedIdiom}
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
            idiom={displayedIdiom}
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
