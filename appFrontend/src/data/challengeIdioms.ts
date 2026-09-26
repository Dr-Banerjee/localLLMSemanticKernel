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

export function idiomsForFinalQuiz(): ChallengeIdiom[] {
  const startId = challengeIdiomCount - checkpointInterval + 1;
  return challengeIdioms.filter((idiom) => idiom.id >= startId && idiom.id <= challengeIdiomCount);
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
