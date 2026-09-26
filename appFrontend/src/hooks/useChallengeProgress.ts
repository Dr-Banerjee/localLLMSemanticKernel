import { mutationOptions, useMutation, useQuery } from "@tanstack/react-query";
import { fetchOrCreateChallengeProgress, updateChallengeProgress } from "../api/challenge";
import { challengeKeys } from "../api/queryKeys";

export function useChallengeProgress() {
  return useQuery({
    queryKey: challengeKeys.progress,
    queryFn: ({ signal }) => fetchOrCreateChallengeProgress({ signal }),
  });
}

export function advanceChallengeStepMutationOptions() {
  return mutationOptions({
    mutationFn: (challengeStep: number) => updateChallengeProgress(challengeStep),
    onSuccess: (progress, _challengeStep, _onMutateResult, { client }) => {
      client.setQueryData(challengeKeys.progress, progress);
    },
  });
}

export function useAdvanceChallengeStep() {
  return useMutation(advanceChallengeStepMutationOptions());
}
