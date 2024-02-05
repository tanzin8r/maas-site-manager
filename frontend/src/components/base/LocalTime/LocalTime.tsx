import type { TimeZone } from "@/api/client";
import { getTimeInTimezone, getTimezoneUTCString } from "@/utils";

const LocalTime = ({ timezone }: { timezone: TimeZone }) => {
  return (
    <>
      {getTimeInTimezone(new Date(), timezone)} UTC{getTimezoneUTCString(timezone)}
    </>
  );
};

export default LocalTime;
