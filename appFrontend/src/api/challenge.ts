import { HttpStatusCode } from "axios";
import { appLanguage } from "../i18n";
import { ApiError } from "./errors";
import { createConversationId } from "../utils/chat";
import { axiosClient } from "./axiosClient";
import type { ChallengeProgress, ConversationMessage } from "../types";

type RequestOptions = {
  signal?: AbortSignal;
};

export async function fetchChallengeProgress({
  signal,
}: RequestOptions = {}): Promise<ChallengeProgress> {
  const { data } = await axiosClient.get<ChallengeProgress>("/api/challenge/get", { signal });
  return data;
}

export async function createChallengeProgress(
  challengeStep: number,
  { signal }: RequestOptions = {},
): Promise<ChallengeProgress> {
  const { data } = await axiosClient.post<ChallengeProgress>(
    "/api/challenge/create",
    { challenge_step: challengeStep },
    { signal },
  );
  return data;
}

export async function updateChallengeProgress(challengeStep: number): Promise<ChallengeProgress> {
  const { data } = await axiosClient.patch<ChallengeProgress>("/api/challenge/update", {
    challenge_step: challengeStep,
  });
  return data;
}

const missingConversationDetail = "Conversation not found";

export type VisitedChallengeNode = {
  conversationId: number;
  messages: ConversationMessage[];
};

export async function getVisitedChallengeNode(
  nodeId: number,
  { signal }: RequestOptions = {},
): Promise<VisitedChallengeNode> {
  const { data } = await axiosClient.get<VisitedChallengeNode>(
    `/api/challenge/visited/${nodeId}`,
    { signal },
  );
  return data;
}

export function isMissingChallengeConversation(error: unknown): boolean {
  return (
    error instanceof ApiError &&
    error.status === HttpStatusCode.NotFound &&
    error.detail === missingConversationDetail
  );
}

export async function startChallengeNode(
  nodeId: number,
  { signal }: RequestOptions = {},
): Promise<{ conversation_id: number }> {
  const conversationId = createConversationId();
  const { data } = await axiosClient.post<{ conversation_id: number }>(
    "/api/challenge/node",
    { node_id: nodeId, conversation_id: conversationId, language: appLanguage() },
    { signal },
  );
  return data;
}

export async function fetchOrCreateChallengeProgress({
  signal,
}: RequestOptions = {}): Promise<ChallengeProgress> {
  try {
    return await fetchChallengeProgress({ signal });
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== HttpStatusCode.NotFound) {
      throw error;
    }
  }

  try {
    return await createChallengeProgress(1, { signal });
  } catch (error) {
    if (error instanceof ApiError && error.status === HttpStatusCode.Conflict) {
      return fetchChallengeProgress({ signal });
    }
    throw error;
  }
}
