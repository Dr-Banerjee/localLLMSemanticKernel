import type { FeaturedIdiom } from "../types";

export const featuredIdioms: FeaturedIdiom[] = [
  {
    phrase: "Break the ice",
    hintKey: "featured.breakTheIce",
    emoji: "🧊",
    accent: "sky",
  },
  {
    phrase: "Piece of cake",
    hintKey: "featured.pieceOfCake",
    emoji: "🍰",
    accent: "rose",
  },
  {
    phrase: "Hit the books",
    hintKey: "featured.hitTheBooks",
    emoji: "📚",
    accent: "violet",
  },
  {
    phrase: "Raining cats and dogs",
    hintKey: "featured.rainingCatsAndDogs",
    emoji: "🌧️",
    accent: "mint",
  },
  {
    phrase: "Butterflies in my stomach",
    hintKey: "featured.butterflies",
    emoji: "🦋",
    accent: "peach",
  },
  {
    phrase: "Let the cat out of the bag",
    hintKey: "featured.letTheCatOut",
    emoji: "🐱",
    accent: "amber",
  },
];

export const followUpPromptKeys = [
  "followUp.anotherExample",
  "followUp.whenToSay",
  "followUp.whyThatWay",
  "followUp.tinyStory",
  "followUp.similarSaying",
] as const;
