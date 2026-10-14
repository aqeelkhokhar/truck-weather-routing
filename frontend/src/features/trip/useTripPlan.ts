import { useCallback, useRef, useState } from "react";
import { ApiError, planTrip } from "../../api/client";
import type { TripPlan, TripRequest } from "../../api/types";

interface TripPlanState {
  plan: TripPlan | null;
  loading: boolean;
  errors: string[];
  submit: (request: TripRequest) => Promise<void>;
}

export function useTripPlan(): TripPlanState {
  const [plan, setPlan] = useState<TripPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const controller = useRef<AbortController | null>(null);

  const submit = useCallback(async (request: TripRequest) => {
    controller.current?.abort();
    const current = new AbortController();
    controller.current = current;
    setLoading(true);
    setErrors([]);
    try {
      setPlan(await planTrip(request, current.signal));
    } catch (error) {
      if (current.signal.aborted) return;
      setErrors(error instanceof ApiError ? error.messages : ["Something went wrong."]);
    } finally {
      if (controller.current === current) setLoading(false);
    }
  }, []);

  return { plan, loading, errors, submit };
}
