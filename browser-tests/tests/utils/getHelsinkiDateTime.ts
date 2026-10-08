// Format an instant as Helsinki time, independent of the machine's time zone:
const helsinkiFormatter = new Intl.DateTimeFormat(
  "en-GB", // To use normal Latin digits
  {
    timeZone: "Europe/Helsinki",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hourCycle: "h23", // Use 00 instead of 24 for midnight
  },
);

/**
 * Formats an instant as Helsinki date and time.
 * The returned format is accepted e.g. by Django admin date/time inputs.
 *
 * @param instant The point in time to format.
 * @returns `date` as YYYY-MM-DD and `time` as HH:MM:SS (24-hour clock).
 */
export default function getHelsinkiDateTime(instant: Date): {
  date: string;
  time: string;
} {
  const parts: Record<string, string> = {};
  for (const { type, value } of helsinkiFormatter.formatToParts(instant)) {
    parts[type] = value;
  }

  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    time: `${parts.hour}:${parts.minute}:${parts.second}`,
  };
}
