import humanInterval from "human-interval";

function intervalToDuration(ms: number) {
  let seconds = Math.floor(ms / 1000);
  const days = Math.floor(seconds / (24 * 3600));
  seconds %= 24 * 3600;
  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;
  const minutes = Math.floor(seconds / 60);
  seconds %= 60;
  return {
    days,
    hours,
    minutes,
    seconds,
  };
}

// return ISO 8601 duration only using days, hours, minutes and seconds
export const humanIntervalToISODuration = (intervalString: string) => {
  const intervalNumber = humanInterval(intervalString);
  if (intervalNumber) {
    const duration = intervalToDuration(intervalNumber);
    return `P${duration.days}DT${duration.hours}H${duration.minutes}M${duration.seconds}S`;
  }
};
