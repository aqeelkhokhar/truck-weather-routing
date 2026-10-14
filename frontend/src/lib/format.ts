const SECONDS_PER_MINUTE = 60;
const MINUTES_PER_HOUR = 60;

export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / SECONDS_PER_MINUTE);
  const hours = Math.floor(totalMinutes / MINUTES_PER_HOUR);
  const minutes = totalMinutes % MINUTES_PER_HOUR;
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`;
}

export function formatMiles(miles: number): string {
  return `${Math.round(miles).toLocaleString("en-US")} mi`;
}

export function formatDateTime(iso: string): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso));
}

export function toLocalInputValue(date: Date): string {
  const offsetMs = date.getTimezoneOffset() * SECONDS_PER_MINUTE * 1000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

export function addHours(iso: string, hours: number): string {
  return new Date(
    new Date(iso).getTime() + hours * MINUTES_PER_HOUR * SECONDS_PER_MINUTE * 1000,
  ).toISOString();
}
