export type ReadingPlanSummary = {
  id: string;
  name: string;
  description: string | null;
  durationDays: number;
};

export type ReadingPassage = {
  bookId: string;
  chapterStart: number;
  chapterEnd: number;
};

export type ReadingPlanEntry = {
  dayNumber: number;
  passages: ReadingPassage[];
};

export type StreakInfo = {
  count: number;
  asOfDate: string | null; // YYYY-MM-DD in UTC
};

export type ActiveReadingPlan = {
  plan: ReadingPlanSummary;
  startedAt: string; // ISO timestamp
  today: { dayNumber: number; passages: ReadingPassage[]; completed: boolean };
  progress: { completedDays: number; totalDays: number };
  streak: StreakInfo;
};

export type StartReadingPlanResponse = ActiveReadingPlan | null;

export type CompleteReadingDayResponse = {
  ok: true;
  alreadyCompleted: boolean;
  active: ActiveReadingPlan | null;
};

