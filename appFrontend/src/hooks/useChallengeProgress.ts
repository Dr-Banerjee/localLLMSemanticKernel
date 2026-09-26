import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchOrCreateChallengeProgress, updateChallengeProgress } from "../api/challenge";
import { challengeKeys } from "../api/queryKeys";

export function useChallengeProgress() {
  return useQuery({
    queryKey: challengeKeys.progress,
    queryFn: ({ signal }) => fetchOrCreateChallengeProgress({ signal }),
  });
}

export function useAdvanceChallengeStep() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (challengeStep: number) => updateChallengeProgress(challengeStep),
    onSuccess: (progress) => {
      queryClient.setQueryData(challengeKeys.progress, progress);
    },
  });
}
