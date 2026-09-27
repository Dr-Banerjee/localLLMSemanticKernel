import rawIdioms from "../utils/challenge_idioms.json" with { type: "json" };

export type ChallengeIdiom = {
  id: number;
  idiom: string;
  meaning: string;
  nomenclature_reason: string;
  example: string;
  correct_sentence: string;
  wrong_sentence: string;
  remember: string;
  rarity: number;
};

export const checkpointInterval = 9;
export const checkpointPassScore = 4;

export function isCheckpoint(id: number): boolean {
  return id > 0 && id % checkpointInterval === 0;
}

export function isStoneBeforeCheckpoint(id: number): boolean {
  const checkpointId = id + 1;
  return checkpointId % checkpointInterval === 0 && checkpointId !== challengeIdiomCount;
}

export function idiomPathIndex(id: number): number {
  const quizzesBefore =
    Math.floor(id / checkpointInterval) - (id >= challengeIdiomCount ? 1 : 0);
  return id - 1 + quizzesBefore;
}

export const challengeIdioms: ChallengeIdiom[] = [...rawIdioms].sort(
  (left, right) => left.id - right.id,
);

export const challengeIdiomCount = challengeIdioms.length;

export function idiomsBeforeCheckpoint(stoneId: number): ChallengeIdiom[] {
  const previousCheckpoint = stoneId - (stoneId % checkpointInterval);
  const startId = previousCheckpoint === 0 ? 1 : previousCheckpoint;
  return challengeIdioms.filter((idiom) => idiom.id >= startId && idiom.id <= stoneId);
}

export function idiomsForCheckpointQuiz(checkpointId: number): ChallengeIdiom[] {
  return idiomsBeforeCheckpoint(checkpointId - 1);
}

export type NextChallengeTarget =
  | { kind: "quiz"; checkpointId: number }
  | { kind: "idiom"; idiom: ChallengeIdiom };

function quizAlreadyPassed(checkpointId: number, clearedThrough: number): boolean {
  return clearedThrough >= checkpointId;
}

export function nextChallengeTarget(
  idiomId: number,
  clearedThrough: number,
): NextChallengeTarget | null {
  const quizCheckpoint = isStoneBeforeCheckpoint(idiomId)
    ? idiomId + 1
    : idiomId === challengeIdiomCount
      ? challengeIdiomCount
      : null;

  if (quizCheckpoint !== null && !quizAlreadyPassed(quizCheckpoint, clearedThrough)) {
    return { kind: "quiz", checkpointId: quizCheckpoint };
  }

  const next = challengeIdioms.find((entry) => entry.id === idiomId + 1);
  return next ? { kind: "idiom", idiom: next } : null;
}

export function idiomsForFinalQuiz(): ChallengeIdiom[] {
  const startId = challengeIdiomCount - checkpointInterval + 1;
  return challengeIdioms.filter((idiom) => idiom.id >= startId && idiom.id <= challengeIdiomCount);
}

export function clearedCheckpointStorageKey(userId: string): string {
  return `pip-checkpoint-quiz:${userId}`;
}

export function readClearedCheckpoint(userId: string): number {
  const value = Number(localStorage.getItem(clearedCheckpointStorageKey(userId)));
  return Number.isInteger(value) && value > 0 ? value : 0;
}

export function writeClearedCheckpoint(userId: string, through: number): void {
  localStorage.setItem(clearedCheckpointStorageKey(userId), String(through));
}

export function formatChallengeExplanation(idiom: ChallengeIdiom): string {
  return [
    `Meaning: ${idiom.meaning}`,
    "Why does it mean that?",
    idiom.nomenclature_reason,
    "Example:",
    idiom.example,
    "Remember:",
    idiom.remember,
  ].join("\n");
}
