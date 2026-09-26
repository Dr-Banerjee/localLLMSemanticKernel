import { Fragment, useEffect, useRef, useState } from "react";
import { messageForApiError } from "../api/errors";
import {
  challengeIdiomCount,
  challengeIdioms,
  checkpointInterval,
  idiomPathIndex,
  idiomsForCheckpointQuiz,
  idiomsForFinalQuiz,
  isCheckpoint,
  isStoneBeforeCheckpoint,
  type ChallengeIdiom,
} from "../data/challengeIdioms";
import { useAdvanceChallengeStep, useChallengeProgress } from "../hooks/useChallengeProgress";
import { Birdhouse, houseName, Tree } from "./ChallengeScenery";
import { CheckpointQuiz } from "./CheckpointQuiz";
import { Mascot } from "./Mascot";
import styles from "./ChallengePathScreen.module.css";

type ChallengePathScreenProps = {
  onBackHome: () => void;
  onOpenIdiom: (idiom: ChallengeIdiom) => Promise<void>;
};

type NodeState = "done" | "current" | "locked";

function clearedStorageKey(userId: string): string {
  return `pip-checkpoint-quiz:${userId}`;
}

function readClearedThrough(userId: string): number {
  const value = Number(localStorage.getItem(clearedStorageKey(userId)));
  return Number.isInteger(value) && value > 0 ? value : 0;
}

function nodeState(id: number, step: number): NodeState {
  if (id < step) {
    return "done";
  }
  if (id === step) {
    return "current";
  }
  return "locked";
}

function idiomNodeState(id: number, step: number, quizBlocking: boolean): NodeState {
  if (quizBlocking && id === step) {
    return "locked";
  }
  return nodeState(id, step);
}

function quizNodeState(checkpointId: number, step: number, clearedThrough: number): NodeState {
  if (step > checkpointId || (step === checkpointId && clearedThrough >= checkpointId)) {
    return "done";
  }
  if (step === checkpointId) {
    return "current";
  }
  return "locked";
}

function sideClass(pathIndex: number): string {
  return pathIndex % 2 === 0 ? styles.left : styles.right;
}

function rewardTeaser(step: number): string {
  if (step > challengeIdiomCount) {
    return "Pip visited every saying. The whole nest is glowing!";
  }

  if (step === challengeIdiomCount) {
    return `Finish this saying. The last quiz then opens the way to ${houseName(challengeIdiomCount / checkpointInterval)}.`;
  }

  for (let id = step + 1; id <= challengeIdiomCount; id += 1) {
    const hops = id - step;
    const hopLabel = hops === 1 ? "the next stone" : `${hops} sayings ahead`;
    if (id % checkpointInterval === 0) {
      if (hops === 1) {
        return `A quiz stone is waiting before ${houseName(id / checkpointInterval)}.`;
      }
      return `${houseName(id / checkpointInterval)} is waiting at ${hopLabel}.`;
    }
    if (id % 3 === 0) {
      return `A little tree for Pip is ${hopLabel}.`;
    }
  }

  return "Keep hopping. Pip loves a curious friend.";
}

export function ChallengePathScreen({
  onBackHome,
  onOpenIdiom,
}: ChallengePathScreenProps) {
  const progressQuery = useChallengeProgress();
  const advanceStep = useAdvanceChallengeStep();
  const currentRef = useRef<HTMLLIElement>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [encouragement, setEncouragement] = useState<string | null>(null);
  const [isOpening, setIsOpening] = useState(false);
  const [activeCheckpoint, setActiveCheckpoint] = useState<number | null>(null);
  const [clearedForUser, setClearedForUser] = useState<{
    userId: string;
    through: number;
  } | null>(null);
  const progress = progressQuery.data;
  const step = progress?.challenge_step ?? 1;
  const userId = progress?.user_id;

  let clearedThrough = 0;
  if (userId) {
    if (clearedForUser?.userId === userId) {
      clearedThrough = clearedForUser.through;
    } else {
      clearedThrough = readClearedThrough(userId);
      setClearedForUser({ userId, through: clearedThrough });
    }
  }
  const quizBlocking =
    isCheckpoint(step) && step < challengeIdiomCount && clearedThrough < step;
  const onFinalQuiz = step > challengeIdiomCount && clearedThrough < challengeIdiomCount;
  const atFinalHouse = step > challengeIdiomCount && clearedThrough >= challengeIdiomCount;
  const castleName = houseName(challengeIdiomCount / checkpointInterval);

  useEffect(() => {
    currentRef.current?.scrollIntoView({ block: "center" });
  }, [progress?.challenge_step, quizBlocking, onFinalQuiz, atFinalHouse]);

  async function continueToLesson(idiom: ChallengeIdiom, advance: boolean) {
    if (!progress) {
      return;
    }

    setActionError(null);
    setIsOpening(true);
    try {
      if (advance && progress.challenge_step === idiom.id) {
        await advanceStep.mutateAsync(idiom.id + 1);
      }
      await onOpenIdiom(idiom);
    } catch (error) {
      setActionError(messageForApiError(error));
    } finally {
      setIsOpening(false);
    }
  }

  function openNode(idiom: ChallengeIdiom) {
    if (!progress || isOpening) {
      return;
    }

    const state = idiomNodeState(idiom.id, progress.challenge_step, quizBlocking);
    if (state === "locked") {
      return;
    }

    setEncouragement(null);
    void continueToLesson(idiom, state === "current");
  }

  function openQuiz(checkpointId: number) {
    if (quizNodeState(checkpointId, step, clearedThrough) !== "current" || isOpening) {
      return;
    }
    setActionError(null);
    setEncouragement(null);
    setActiveCheckpoint(checkpointId);
  }

  function openFinalQuiz() {
    if (!onFinalQuiz || isOpening) {
      return;
    }
    setActionError(null);
    setEncouragement(null);
    setActiveCheckpoint(challengeIdiomCount);
  }

  function passQuiz() {
    if (!userId || activeCheckpoint === null) {
      return;
    }
    const next = Math.max(clearedThrough, activeCheckpoint);
    localStorage.setItem(clearedStorageKey(userId), String(next));
    setClearedForUser({ userId, through: next });
    setActiveCheckpoint(null);
  }

  function leaveQuiz() {
    if (activeCheckpoint === null) {
      return;
    }
    const house = houseName(
      activeCheckpoint === challengeIdiomCount
        ? challengeIdiomCount / checkpointInterval
        : activeCheckpoint / checkpointInterval,
    );
    setEncouragement(
      activeCheckpoint === challengeIdiomCount
        ? `Pip is not ready for ${house} yet. That grand birdhouse is the end of the path. Revisit the stones behind you to freshen up, then try the last test again.`
        : `Pip is not ready for ${house} yet. Revisit the stones behind you to freshen up, then try the test again.`,
    );
    setActiveCheckpoint(null);
  }

  if (activeCheckpoint !== null) {
    return (
      <CheckpointQuiz
        idioms={
          activeCheckpoint === challengeIdiomCount
            ? idiomsForFinalQuiz()
            : idiomsForCheckpointQuiz(activeCheckpoint)
        }
        houseLabel={houseName(
          activeCheckpoint === challengeIdiomCount
            ? challengeIdiomCount / checkpointInterval
            : activeCheckpoint / checkpointInterval,
        )}
        finale={activeCheckpoint === challengeIdiomCount}
        busy={false}
        error={null}
        onPass={passQuiz}
        onFail={leaveQuiz}
        onCancel={() => {
          setActiveCheckpoint(null);
        }}
      />
    );
  }

  const reachedSaying = quizBlocking ? step - 1 : Math.min(step, challengeIdiomCount);

  return (
    <section className={styles.screen}>
      <header className={styles.header}>
        <button className={styles.back} type="button" onClick={onBackHome}>
          Back to the nest
        </button>
        <p className={styles.kicker}>Pip’s journey</p>
        <h1>Pip's idiom Challenge</h1>
        <p className={styles.lead}>
          Hop with Pip from the first idiom to the last. A quiz stone sits before each
          birdhouse, and one last test waits after the final saying. You can open the stone
          Pip is standing on, and the stones already behind.
        </p>
        {progress ? (
          <>
            <p className={styles.progress}>
              {onFinalQuiz
                ? `Pip is on the last test before ${castleName}`
                : atFinalHouse
                  ? `Pip reached ${castleName}`
                  : quizBlocking
                    ? `Pip is on the test before ${houseName(step / checkpointInterval)}`
                    : `Pip is on saying ${reachedSaying} of ${challengeIdiomCount}`}
            </p>
            <div
              className={styles.meter}
              role="progressbar"
              aria-valuemin={1}
              aria-valuemax={challengeIdiomCount}
              aria-valuenow={Math.max(reachedSaying, 1)}
              aria-label="Sayings Pip has reached"
            >
              <span
                style={{
                  width: `${(Math.max(reachedSaying, 1) / challengeIdiomCount) * 100}%`,
                }}
              />
            </div>
            <p className={styles.teaser}>
              {onFinalQuiz
                ? `Pass the last test to reach ${castleName}, the grand birdhouse at the end of the path.`
                : atFinalHouse
                  ? `${castleName} is the end of the path. The whole nest is glowing!`
                  : quizBlocking
                    ? `Pass the short test to reach ${houseName(step / checkpointInterval)}.`
                    : rewardTeaser(step)}
            </p>
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

      {encouragement ? (
        <div className={styles.teaser} role="status">
          <p>{encouragement}</p>
        </div>
      ) : null}

      {progress ? (
        <ol className={styles.trail}>
          {challengeIdioms.map((idiom) => {
            const state = idiomNodeState(idiom.id, step, quizBlocking);
            const locked = state === "locked";
            const reward =
              idiom.id === challengeIdiomCount
                ? null
                : idiom.id % checkpointInterval === 0
                  ? "house"
                  : idiom.id % 3 === 0
                    ? "tree"
                    : null;
            const label = locked
              ? `Saying ${idiom.id}, still ahead`
              : `Saying ${idiom.id}, ${idiom.idiom}${state === "current" ? ", Pip is here" : ""}`;
            const pathIndex = idiomPathIndex(idiom.id);
            const checkpointId = idiom.id + 1;
            const quizState = isStoneBeforeCheckpoint(idiom.id)
              ? quizNodeState(checkpointId, step, clearedThrough)
              : null;

            return (
              <Fragment key={idiom.id}>
                <li
                  ref={state === "current" ? currentRef : undefined}
                  className={`${styles.stop} ${styles[state]} ${sideClass(pathIndex)}`}
                >
                  {pathIndex > 0 ? <span className={styles.connector} aria-hidden="true" /> : null}
                  {reward === "house" ? (
                    <Birdhouse level={idiom.id / checkpointInterval} locked={locked} />
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
                      disabled={locked || isOpening}
                      aria-label={label}
                      onClick={() => {
                        openNode(idiom);
                      }}
                    >
                      <span className={styles.number}>{idiom.id}</span>
                      {locked ? null : <span className={styles.phrase}>{idiom.idiom}</span>}
                    </button>
                  </div>
                </li>
                {quizState ? (
                  <li
                    ref={quizState === "current" ? currentRef : undefined}
                    className={`${styles.stop} ${styles.quiz} ${styles[quizState]} ${sideClass(pathIndex + 1)}`}
                  >
                    <span className={styles.connector} aria-hidden="true" />
                    <div className={styles.stoneWrap}>
                      {quizState === "current" ? (
                        <Mascot mood="think" className={`${styles.pip} ${styles.pipOnStone}`} />
                      ) : null}
                      <button
                        type="button"
                        className={styles.stone}
                        disabled={quizState !== "current" || isOpening}
                        aria-label={
                          quizState === "locked"
                            ? `Test before ${houseName(checkpointId / checkpointInterval)}, still ahead`
                            : `Test before ${houseName(checkpointId / checkpointInterval)}${quizState === "current" ? ", Pip is here" : ""}`
                        }
                        onClick={() => {
                          openQuiz(checkpointId);
                        }}
                      >
                        <span className={styles.number}>?</span>
                        {quizState === "locked" ? null : (
                          <span className={styles.phrase}>Short test</span>
                        )}
                      </button>
                    </div>
                  </li>
                ) : null}
              </Fragment>
            );
            })}
          <li
            ref={onFinalQuiz ? currentRef : undefined}
            className={`${styles.stop} ${styles.quiz} ${onFinalQuiz ? styles.current : atFinalHouse ? styles.done : styles.locked} ${sideClass(idiomPathIndex(challengeIdiomCount) + 1)}`}
          >
            <span className={styles.connector} aria-hidden="true" />
            <div className={styles.stoneWrap}>
              {onFinalQuiz ? (
                <Mascot mood="think" className={`${styles.pip} ${styles.pipOnStone}`} />
              ) : null}
              <button
                type="button"
                className={styles.stone}
                disabled={!onFinalQuiz || isOpening}
                aria-label={
                  onFinalQuiz
                    ? `Last test before ${castleName}, Pip is here`
                    : atFinalHouse
                      ? `Last test before ${castleName}`
                      : `Last test before ${castleName}, still ahead`
                }
                onClick={openFinalQuiz}
              >
                <span className={styles.number}>?</span>
                {onFinalQuiz || atFinalHouse ? (
                  <span className={styles.phrase}>Last test</span>
                ) : null}
              </button>
            </div>
          </li>
          <li
            ref={atFinalHouse ? currentRef : undefined}
            className={`${styles.stop} ${atFinalHouse ? styles.current : styles.locked} ${sideClass(idiomPathIndex(challengeIdiomCount) + 2)}`}
            aria-label={
              atFinalHouse ? `${castleName}, Pip is here` : `${castleName}, still ahead`
            }
          >
            <span className={styles.connector} aria-hidden="true" />
            <Birdhouse
              level={challengeIdiomCount / checkpointInterval}
              locked={!atFinalHouse}
            />
            {atFinalHouse ? (
              <div className={styles.stoneWrap}>
                <Mascot mood="cheer" className={`${styles.pip} ${styles.pipInHouse}`} />
              </div>
            ) : null}
          </li>
        </ol>
      ) : null}
    </section>
  );
}
