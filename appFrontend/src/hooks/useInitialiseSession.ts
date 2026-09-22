import { queryOptions, useQuery } from "@tanstack/react-query";
import { sessionKeys } from "../api/queryKeys";
import { SessionService } from "../services/sessionService";

const sessionService = new SessionService();

export function sessionQueryOptions() {
  return queryOptions({
    queryKey: sessionKeys.current,
    queryFn: ({ signal }) => sessionService.initialiseSession(signal),
    staleTime: Infinity,
    retry: 1,
  });
}

export function useInitialiseSession() {
  return useQuery(sessionQueryOptions());
}
