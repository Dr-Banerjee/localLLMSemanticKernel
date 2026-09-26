import { HttpStatusCode } from "axios";
import { ApiError } from "./errors";
import { axiosClient } from "./axiosClient";
import type { ChallengeProgress, ConversationMessage } from "../types";

type RequestOptions = {
  signal?: AbortSignal;
};

export type ChallengeProgressLoad = {
  progress: ChallengeProgress;
  newlyCreated: boolean;
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

export async function fetchVisitedChallengeNode(
  nodeId: number,
): Promise<{ conversationId: number; messages: ConversationMessage[] }> {
  const { data } = await axiosClient.get<{
    conversationId: number;
    messages: ConversationMessage[];
  }>(`/api/challenge/visited/${nodeId}`);
  return data;
}

export async function startChallengeNode(
  nodeId: number,
  { signal }: RequestOptions = {},
): Promise<{ conversation_id: number }> {
  const { data } = await axiosClient.post<{ conversation_id: number }>(
    "/api/challenge/node",
    { node_id: nodeId },
    { signal },
  );
  return data;
}

export async function fetchOrCreateChallengeProgress({
  signal,
}: RequestOptions = {}): Promise<ChallengeProgressLoad> {
  try {
    const progress = await fetchChallengeProgress({ signal });
    return { progress, newlyCreated: false };
  } catch (error) {
    if (!(error instanceof ApiError) || error.status !== HttpStatusCode.NotFound) {
      throw error;
    }
  }

  try {
    const progress = await createChallengeProgress(1, { signal });
    return { progress, newlyCreated: true };
  } catch (error) {
    if (error instanceof ApiError && error.status === HttpStatusCode.Conflict) {
      const progress = await fetchChallengeProgress({ signal });
      return { progress, newlyCreated: false };
    }
    throw error;
  }
}
