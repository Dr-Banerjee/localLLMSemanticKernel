import rawIdioms from "../utils/challenge_idioms.json" with { type: "json" };

export type ChallengeIdiom = {
  id: number;
  idiom: string;
  meaning: string;
  nomenclature_reason: string;
  example: string;
  remember: string;
  rarity: number;
};

export const challengeIdioms: ChallengeIdiom[] = [...rawIdioms].sort(
  (left, right) => left.id - right.id,
);

export const challengeIdiomCount = challengeIdioms.length;

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
