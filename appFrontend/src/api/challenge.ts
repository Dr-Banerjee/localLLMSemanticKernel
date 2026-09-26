import { HttpStatusCode } from "axios";
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

async function getVisitedChallengeNode(
  nodeId: number,
): Promise<{ conversationId: number; messages: ConversationMessage[] }> {
  const { data } = await axiosClient.get<{
    conversationId: number;
    messages: ConversationMessage[];
  }>(`/api/challenge/visited/${nodeId}`);
  return data;
}

function isMissingChallengeConversation(error: unknown): boolean {
  return (
    error instanceof ApiError &&
    error.status === HttpStatusCode.NotFound &&
    error.detail === missingConversationDetail
  );
}

export async function fetchVisitedChallengeNode(
  nodeId: number,
  startNode: (nodeId: number) => Promise<{ conversation_id: number }> = startChallengeNode,
): Promise<{ conversationId: number; messages: ConversationMessage[] }> {
  try {
    return await getVisitedChallengeNode(nodeId);
  } catch (error) {
    if (!isMissingChallengeConversation(error)) {
      throw error;
    }
  }

  await startNode(nodeId);
  return getVisitedChallengeNode(nodeId);
}

export async function startChallengeNode(
  nodeId: number,
  { signal }: RequestOptions = {},
): Promise<{ conversation_id: number }> {
  const conversationId = createConversationId();
  const { data } = await axiosClient.post<{ conversation_id: number }>(
    "/api/challenge/node",
    { node_id: nodeId, conversation_id: conversationId },
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
