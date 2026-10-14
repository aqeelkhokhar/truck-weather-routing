import type { TripPlan, TripRequest } from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  readonly messages: string[];

  constructor(messages: string[]) {
    super(messages.join(" "));
    this.messages = messages;
  }
}

function collectMessages(payload: unknown): string[] {
  if (typeof payload === "string") return [payload];
  if (Array.isArray(payload)) return payload.flatMap(collectMessages);
  if (payload && typeof payload === "object") {
    return Object.entries(payload).flatMap(([field, value]) =>
      collectMessages(value).map((message) =>
        field === "detail" || field === "non_field_errors" ? message : `${field}: ${message}`,
      ),
    );
  }
  return [];
}

export async function planTrip(request: TripRequest, signal?: AbortSignal): Promise<TripPlan> {
  let response: Response;
  try {
    response = await fetch(`${API_URL}/api/plan/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") throw error;
    throw new ApiError(["The routing service could not be reached."]);
  }
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => null);
    const messages = collectMessages(payload);
    throw new ApiError(messages.length ? messages : ["The trip could not be planned."]);
  }
  return (await response.json()) as TripPlan;
}
