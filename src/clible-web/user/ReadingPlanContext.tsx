import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { useAuth } from '../AuthContext';
import type {
  ActiveReadingPlan,
  CompleteReadingDayResponse,
  ReadingPlanSummary,
  StartReadingPlanResponse,
} from '../types/reading';

type ReadingPlanContextType = {
  plans: ReadingPlanSummary[];
  active: ActiveReadingPlan | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  startPlan: (planId: string) => Promise<void>;
  completeDay: (dayNumber: number) => Promise<void>;
  abandonActive: () => Promise<void>;
};

const ReadingPlanContext = createContext<ReadingPlanContextType | null>(null);

async function readErrorMessage(resp: Response): Promise<string | null> {
  const body = (await resp.json().catch(() => ({}))) as { error?: string };
  return typeof body.error === 'string' ? body.error : null;
}

export function ReadingPlanProvider({ children }: { children: ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [plans, setPlans] = useState<ReadingPlanSummary[]>([]);
  const [active, setActive] = useState<ActiveReadingPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);

    const [plansRes, activeRes] = await Promise.all([
      fetch('/api/user/reading/plans'),
      fetch('/api/user/reading/active'),
    ]);

    if (!plansRes.ok) {
      const msg = (await readErrorMessage(plansRes)) ?? 'Failed to load reading plans.';
      setError(msg);
      setLoading(false);
      throw new Error(msg);
    }
    if (!activeRes.ok) {
      const msg = (await readErrorMessage(activeRes)) ?? 'Failed to load active reading plan.';
      setError(msg);
      setLoading(false);
      throw new Error(msg);
    }

    const plansData = (await plansRes.json()) as ReadingPlanSummary[];
    const activeData = (await activeRes.json()) as ActiveReadingPlan | null;
    setPlans(plansData);
    setActive(activeData);
    setLoading(false);
  };

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      setPlans([]);
      setActive(null);
      setLoading(false);
      setError(null);
      return;
    }

    const ac = new AbortController();
    setLoading(true);
    setError(null);

    Promise.all([
      fetch('/api/user/reading/plans', { signal: ac.signal }),
      fetch('/api/user/reading/active', { signal: ac.signal }),
    ])
      .then(async ([plansRes, activeRes]) => {
        if (!plansRes.ok) {
          const msg = (await readErrorMessage(plansRes)) ?? 'Failed to load reading plans.';
          throw new Error(msg);
        }
        if (!activeRes.ok) {
          const msg =
            (await readErrorMessage(activeRes)) ?? 'Failed to load active reading plan.';
          throw new Error(msg);
        }
        const plansData = (await plansRes.json()) as ReadingPlanSummary[];
        const activeData = (await activeRes.json()) as ActiveReadingPlan | null;
        return { plansData, activeData };
      })
      .then(({ plansData, activeData }) => {
        setPlans(plansData);
        setActive(activeData);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (ac.signal.aborted) return;
        setError(e instanceof Error ? e.message : 'Failed to load reading plan data.');
        setLoading(false);
      });

    return () => ac.abort();
  }, [user, authLoading]);

  const startPlan = async (planId: string) => {
    if (!user) throw new Error('Not authenticated.');
    const resp = await fetch(`/api/user/reading/start/${encodeURIComponent(planId)}`, {
      method: 'POST',
    });
    if (!resp.ok) {
      const msg = (await readErrorMessage(resp)) ?? 'Failed to start reading plan.';
      setError(msg);
      throw new Error(msg);
    }
    const data = (await resp.json()) as StartReadingPlanResponse;
    setActive(data);
  };

  const completeDay = async (dayNumber: number) => {
    if (!user) throw new Error('Not authenticated.');
    const resp = await fetch(`/api/user/reading/complete/${dayNumber}`, { method: 'POST' });
    if (!resp.ok) {
      const msg = (await readErrorMessage(resp)) ?? 'Failed to mark day complete.';
      setError(msg);
      throw new Error(msg);
    }
    const data = (await resp.json()) as CompleteReadingDayResponse;
    setActive(data.active);
  };

  const abandonActive = async () => {
    if (!user) throw new Error('Not authenticated.');
    const resp = await fetch('/api/user/reading/active', { method: 'DELETE' });
    if (!resp.ok) {
      const msg = (await readErrorMessage(resp)) ?? 'Failed to abandon active plan.';
      setError(msg);
      throw new Error(msg);
    }
    setActive(null);
  };

  const value = useMemo<ReadingPlanContextType>(
    () => ({ plans, active, loading, error, reload, startPlan, completeDay, abandonActive }),
    [plans, active, loading, error],
  );

  return <ReadingPlanContext.Provider value={value}>{children}</ReadingPlanContext.Provider>;
}

export function useReadingPlan(): ReadingPlanContextType {
  const ctx = useContext(ReadingPlanContext);
  if (!ctx) {
    throw new Error('useReadingPlan must be used within a ReadingPlanProvider');
  }
  return ctx;
}

