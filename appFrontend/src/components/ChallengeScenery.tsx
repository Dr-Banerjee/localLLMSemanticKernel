import styles from "./ChallengeScenery.module.css";

const houseNames = [
  "Twig Hut",
  "Acorn Nook",
  "Berry Porch",
  "Daisy Cottage",
  "Sunny Stoop",
  "Pebble House",
  "Mossy Manor",
  "Flower Porch",
  "Lantern Home",
  "Honey Cottage",
  "Rose Balcony",
  "Cloud Porch",
  "Buttercup House",
  "Maple Manor",
  "Sunset Nest",
  "Golden Eaves",
  "Amber Door",
  "Jewel Cottage",
  "Sunflower Hall",
  "Gilded Nest",
  "Crown Cottage",
  "Star Step",
  "Moon Balcony",
  "Star Palace",
  "Comet House",
  "Sparkle Manor",
  "Galaxy Nest",
  "Aurora Hall",
  "Wish Palace",
  "Rainbow Castle",
] as const;

export function houseName(level: number): string {
  return houseNames[level - 1] ?? "Birdhouse";
}

type SceneryProps = {
  locked: boolean;
};

export function Tree({ locked }: SceneryProps) {
  return (
    <div className={`${styles.reward} ${locked ? styles.locked : ""}`} aria-hidden="true">
      <svg className={styles.tree} viewBox="0 0 140 110">
        <ellipse cx="70" cy="104" rx="30" ry="6" fill="rgba(58,42,26,0.16)" />
        <rect x="62" y="64" width="16" height="34" rx="6" fill="#6b3f2a" stroke="#3a2a1a" strokeWidth="3" />
        <path d="M28 74h84" stroke="#5a331f" strokeWidth="7" strokeLinecap="round" />
        <circle cx="46" cy="58" r="20" fill="#3d9458" stroke="#215736" strokeWidth="3" />
        <circle cx="96" cy="56" r="18" fill="#8fbc6a" stroke="#215736" strokeWidth="3" />
        <circle cx="70" cy="42" r="28" fill="#2f7d4a" stroke="#215736" strokeWidth="3" />
        <circle cx="80" cy="30" r="7" fill="#d9ffb0" />
      </svg>
      {locked ? null : <p className={styles.caption}>A perch for Pip</p>}
    </div>
  );
}

type BirdhouseProps = SceneryProps & {
  level: number;
};

export function Birdhouse({ level, locked }: BirdhouseProps) {
  const hue = 14 + (level - 1) * 11;
  const wall = `hsl(${hue} 74% ${Math.max(48, 72 - Math.floor(level / 2))}%)`;
  const roof = level >= 16 ? "#ffd45a" : level >= 8 ? "#e05a6f" : "#6b3f2a";
  const door = level >= 18 ? "#f6c453" : "#5a331f";
  const flowerCount = Math.min(6, Math.max(1, Math.floor(level / 2)));

  return (
    <div className={`${styles.reward} ${locked ? styles.locked : ""}`} aria-hidden="true">
      <svg className={styles.house} viewBox="0 0 180 156">
        <ellipse cx="90" cy="148" rx="52" ry="6" fill="rgba(58,42,26,0.16)" />
        {level >= 28 ? (
          <path
            d="M28 36c16-16 32-16 48 0 16-16 32-16 48 0 16-16 32-16 28 0"
            fill="none"
            stroke="#7ec8e3"
            strokeWidth="5"
            strokeLinecap="round"
          />
        ) : null}
        {level >= 20 ? <Turret x={24} wall={wall} roof={roof} /> : null}
        {level >= 24 ? <Turret x={132} wall={wall} roof={roof} /> : null}
        {level >= 5 ? (
          <g>
            <rect x="112" y="40" width="14" height="28" rx="3" fill="#6b3f2a" stroke="#3a2a1a" strokeWidth="3" />
            <rect x="108" y="34" width="22" height="10" rx="3" fill="#5a331f" />
          </g>
        ) : null}
        <polygon points="38,82 90,36 142,82" fill={roof} stroke="#3a2a1a" strokeWidth="4" strokeLinejoin="round" />
        {level >= 16 ? (
          <polygon points="50,76 90,48 130,76" fill="none" stroke="#fffdf6" strokeWidth="3" />
        ) : null}
        {level >= 26 ? <Star cx={90} cy={24} /> : null}
        <rect x="50" y="78" width="80" height="64" rx="10" fill={wall} stroke="#3a2a1a" strokeWidth="4" />
        {level >= 12 ? (
          <rect x="58" y="108" width="64" height="8" rx="3" fill="#fffdf6" stroke="#3a2a1a" strokeWidth="3" />
        ) : null}
        <rect x="78" y="100" width="24" height="42" rx="12" fill={door} stroke="#3a2a1a" strokeWidth="3" />
        {level >= 18 ? <circle cx="95" cy="120" r="3" fill="#fffdf6" /> : null}
        {level >= 2 ? <Window x={60} y={88} /> : null}
        {level >= 6 ? <Window x={106} y={88} /> : null}
        {level >= 9 ? (
          <rect x="56" y="104" width="22" height="6" rx="2" fill="#2f7d4a" stroke="#3a2a1a" strokeWidth="2" />
        ) : null}
        {level >= 8 ? (
          <g>
            <line x1="124" y1="52" x2="124" y2="74" stroke="#3a2a1a" strokeWidth="3" />
            <polygon points="124,52 148,60 124,68" fill="#ffd45a" stroke="#3a2a1a" strokeWidth="2" />
          </g>
        ) : null}
        {level >= 10 ? <Lights y={74} /> : null}
        {level >= 22 ? <Lights y={96} /> : null}
        {Array.from({ length: flowerCount }, (_, index) => (
          <Flower key={index} cx={18 + index * 26} />
        ))}
      </svg>
      {locked ? null : <p className={styles.caption}>{houseName(level)}</p>}
    </div>
  );
}

function Window({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x} y={y} width="16" height="14" rx="3" fill="#d9f4ff" stroke="#3a2a1a" strokeWidth="2" />
      <path d={`M${x + 8} ${y}v14M${x} ${y + 7}h16`} stroke="#3a2a1a" strokeWidth="2" />
    </g>
  );
}

function Turret({ x, wall, roof }: { x: number; wall: string; roof: string }) {
  return (
    <g>
      <rect x={x} y="70" width="24" height="72" rx="6" fill={wall} stroke="#3a2a1a" strokeWidth="3" />
      <polygon points={`${x - 4},72 ${x + 12},48 ${x + 28},72`} fill={roof} stroke="#3a2a1a" strokeWidth="3" />
    </g>
  );
}

function Star({ cx, cy }: { cx: number; cy: number }) {
  return <polygon points={`${cx},${cy - 10} ${cx + 3},${cy - 3} ${cx + 10},${cy - 2} ${cx + 4},${cy + 3} ${cx + 6},${cy + 10} ${cx},${cy + 6} ${cx - 6},${cy + 10} ${cx - 4},${cy + 3} ${cx - 10},${cy - 2} ${cx - 3},${cy - 3}`} fill="#ffd45a" stroke="#3a2a1a" strokeWidth="2" />;
}

function Lights({ y }: { y: number }) {
  return (
    <g>
      <path d={`M46 ${y}q44 16 88 0`} fill="none" stroke="#3a2a1a" strokeWidth="2" />
      <circle cx="62" cy={y + 6} r="4" fill="#ffd45a" />
      <circle cx="90" cy={y + 10} r="4" fill="#e05a6f" />
      <circle cx="118" cy={y + 6} r="4" fill="#7ec8e3" />
    </g>
  );
}

function Flower({ cx }: { cx: number }) {
  return (
    <g>
      <circle cx={cx} cy="140" r="5" fill="#e05a6f" />
      <circle cx={cx} cy="140" r="2" fill="#ffd45a" />
    </g>
  );
}
