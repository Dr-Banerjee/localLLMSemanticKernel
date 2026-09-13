import { useRef, useState } from "react";
import { ApiError, sendConversationMessage } from "./api/client";
import { ConversationScreen } from "./components/ConversationScreen";
import { HomeScreen } from "./components/HomeScreen";
import type { ChatMessage } from "./types";
import { createConversationId, createMessageId } from "./utils/chat";
import styles from "./App.module.css";

function lastUserContent(messages: ChatMessage[]): string | null {
  for (let index = messages.length - 1; index >= 0; index -= 1) {
    if (messages[index].role === "user") {
      return messages[index].content;
    }
  }
  return null;
}

export default function App() {
  const [screen, setScreen] = useState<"home" | "conversation">("home");
  const [idiom, setIdiom] = useState("");
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestTokenRef = useRef(0);

  async function askPip(nextConversationId: number, userInput: string) {
    const token = requestTokenRef.current + 1;
    requestTokenRef.current = token;
    setIsSending(true);
    setError(null);

    try {
      const { response } = await sendConversationMessage(nextConversationId, userInput);
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
      const message =
        caught instanceof ApiError
          ? caught.message
          : "Something wobbled. Let’s try again in a moment!";
      setError(message);
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

    setConversationId(nextConversationId);
    setIdiom(trimmed);
    setMessages([userMessage]);
    setScreen("conversation");
    void askPip(nextConversationId, trimmed);
  }

  function askFollowUp(question: string) {
    const trimmed = question.trim();
    if (!trimmed || isSending || conversationId === null) {
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

  function retryLast() {
    const lastQuestion = lastUserContent(messages);
    if (!lastQuestion || conversationId === null || isSending) {
      return;
    }
    void askPip(conversationId, lastQuestion);
  }

  function resetToHome() {
    requestTokenRef.current += 1;
    setIsSending(false);
    setScreen("home");
    setIdiom("");
    setConversationId(null);
    setMessages([]);
    setError(null);
  }

  return (
    <div className={styles.shell}>
      {screen === "home" ? (
        <HomeScreen onStart={startConversation} />
      ) : (
        <ConversationScreen
          idiom={idiom}
          messages={messages}
          isSending={isSending}
          error={error}
          onAsk={askFollowUp}
          onRetry={retryLast}
          onNewIdiom={resetToHome}
        />
      )}
    </div>
  );
}
