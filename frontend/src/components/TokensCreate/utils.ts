import { formatISODuration, intervalToDuration } from "date-fns";
import humanInterval from "human-interval";

export const humanIntervalToISODuration = (intervalString: string) => {
  const intervalNumber = humanInterval(intervalString);
  if (intervalNumber) {
    return formatISODuration(intervalToDuration({ start: 0, end: intervalNumber }));
  }
};
