import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { startChallengeNode } from "../api/challenge";
import { messageForApiError } from "../api/errors";
import { challengeKeys } from "../api/queryKeys";
import {
  challengeIdiomCount,
  challengeIdioms,
  type ChallengeIdiom,
} from "../data/challengeIdioms";
import { useAdvanceChallengeStep, useChallengeProgress } from "../hooks/useChallengeProgress";
import { Birdhouse, houseName, Tree } from "./ChallengeScenery";
import { Mascot } from "./Mascot";
import styles from "./ChallengePathScreen.module.css";

type ChallengePathScreenProps = {
  onBackHome: () => void;
  onOpenIdiom: (idiom: ChallengeIdiom) => Promise<void>;
  onOpenNewNode: (idiom: ChallengeIdiom) => Promise<void>;
};

type NodeState = "done" | "current" | "next" | "locked";

function nodeState(id: number, step: number): NodeState {
  if (id < step) {
    return "done";
  }
  if (id === step) {
    return "current";
  }
  if (id === step + 1) {
    return "next";
  }
  return "locked";
}

function rewardTeaser(step: number): string {
  if (step >= challengeIdiomCount) {
    return "Pip visited every saying. The whole nest is glowing!";
  }

  for (let id = step + 1; id <= challengeIdiomCount; id += 1) {
    const hops = id - step;
    const hopLabel = hops === 1 ? "the next stone" : `${hops} sayings ahead`;
    if (id % 9 === 0) {
      return `${houseName(id / 9)} is waiting at ${hopLabel}.`;
    }
    if (id % 3 === 0) {
      return `A little tree for Pip is ${hopLabel}.`;
    }
  }

  return "Keep hopping. Pip loves a curious friend.";
}

let initialChallengeNodeStart: Promise<void> | null = null;

export function ChallengePathScreen({
  onBackHome,
  onOpenIdiom,
  onOpenNewNode,
}: ChallengePathScreenProps) {
  const queryClient = useQueryClient();
  const progressQuery = useChallengeProgress();
  const advance = useAdvanceChallengeStep();
  const currentRef = useRef<HTMLLIElement>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [isOpening, setIsOpening] = useState(false);
  const progress = progressQuery.data?.progress;
  const step = progress?.challenge_step ?? 1;

  useEffect(() => {
    currentRef.current?.scrollIntoView({ block: "center" });
  }, [progress?.challenge_step]);

  useEffect(() => {
    if (!progressQuery.data?.newlyCreated || !progress) {
      return;
    }

    if (initialChallengeNodeStart) {
      return;
    }

    initialChallengeNodeStart = startChallengeNode(1)
      .then(() => {
        queryClient.setQueryData(challengeKeys.progress, {
          progress,
          newlyCreated: false,
        });
      })
      .catch((error: unknown) => {
        initialChallengeNodeStart = null;
        setActionError(messageForApiError(error));
      });
  }, [progress, progressQuery.data?.newlyCreated, queryClient]);

  async function openNode(idiom: ChallengeIdiom) {
    if (!progress || advance.isPending || isOpening) {
      return;
    }

    const state = nodeState(idiom.id, progress.challenge_step);
    if (state === "locked") {
      return;
    }

    setActionError(null);
    setIsOpening(true);
    try {
      if (state === "next") {
        await advance.mutateAsync(idiom.id);
        await onOpenNewNode(idiom);
        return;
      }
      await onOpenIdiom(idiom);
    } catch (error) {
      setActionError(messageForApiError(error));
    } finally {
      setIsOpening(false);
    }
  }

  return (
    <section className={styles.screen}>
      <header className={styles.header}>
        <button className={styles.back} type="button" onClick={onBackHome}>
          Back to the nest
        </button>
        <p className={styles.kicker}>Pip’s journey</p>
        <h1>Pip's idiom Challenge</h1>
        <p className={styles.lead}>
          Hop with Pip from the first saying to the last. You can open stones Pip already
          visited, the stone Pip is standing on, and the very next one.
        </p>
        {progress ? (
          <>
            <p className={styles.progress}>
              Pip is on saying {Math.min(step, challengeIdiomCount)} of {challengeIdiomCount}
            </p>
            <div
              className={styles.meter}
              role="progressbar"
              aria-valuemin={1}
              aria-valuemax={challengeIdiomCount}
              aria-valuenow={Math.min(step, challengeIdiomCount)}
              aria-label="Sayings Pip has reached"
            >
              <span style={{ width: `${(Math.min(step, challengeIdiomCount) / challengeIdiomCount) * 100}%` }} />
            </div>
            <p className={styles.teaser}>{rewardTeaser(step)}</p>
          </>
        ) : null}
      </header>

      {progressQuery.isPending ? (
        <p className={styles.status}>Pip is finding the path...</p>
      ) : null}

      {progressQuery.error ? (
        <div className={styles.banner} role="alert">
          <p>Pip couldn’t open the path just now.</p>
          <button
            type="button"
            onClick={() => {
              void progressQuery.refetch();
            }}
          >
            Try again
          </button>
        </div>
      ) : null}

      {actionError ? (
        <div className={styles.banner} role="alert">
          <p>{actionError}</p>
        </div>
      ) : null}

      {progress ? (
        <ol className={styles.trail}>
          {challengeIdioms.map((idiom, index) => {
            const state = nodeState(idiom.id, step);
            const locked = state === "locked";
            const reward =
              idiom.id % 9 === 0 ? "house" : idiom.id % 3 === 0 ? "tree" : null;
            const label = locked
              ? `Saying ${idiom.id}, still ahead`
              : `Saying ${idiom.id}, ${idiom.idiom}${state === "current" ? ", Pip is here" : state === "next" ? ", next hop" : ""}`;

            return (
              <li
                key={idiom.id}
                ref={state === "current" ? currentRef : undefined}
                className={`${styles.stop} ${styles[state]} ${index % 2 === 0 ? styles.left : styles.right}`}
              >
                {index > 0 ? <span className={styles.connector} aria-hidden="true" /> : null}
                {reward === "house" ? (
                  <Birdhouse level={idiom.id / 9} locked={locked} />
                ) : null}
                {reward === "tree" ? <Tree locked={locked} /> : null}
                <div className={styles.stoneWrap}>
                  {state === "current" ? (
                    <Mascot
                      mood={reward === "house" ? "cheer" : "happy"}
                      className={`${styles.pip} ${
                        reward === "house"
                          ? styles.pipInHouse
                          : reward === "tree"
                            ? styles.pipOnTree
                            : styles.pipOnStone
                      }`}
                    />
                  ) : null}
                  <button
                    type="button"
                    className={styles.stone}
                    disabled={locked || advance.isPending || isOpening}
                    aria-label={label}
                    onClick={() => {
                      void openNode(idiom);
                    }}
                  >
                    <span className={styles.number}>{idiom.id}</span>
                    {locked ? null : <span className={styles.phrase}>{idiom.idiom}</span>}
                  </button>
                </div>
              </li>
            );
          })}
        </ol>
      ) : null}
    </section>
  );
}
