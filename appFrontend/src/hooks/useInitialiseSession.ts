import { useQuery } from "@tanstack/react-query";
import { sessionKeys } from "../api/queryKeys";
import { SessionService } from "../services/sessionService";

const sessionService = new SessionService();

export function useInitialiseSession() {
  return useQuery({
    queryKey: sessionKeys.current,
    queryFn: () => sessionService.initialiseSession(),
    staleTime: Infinity,
    retry: 1,
  });
}
