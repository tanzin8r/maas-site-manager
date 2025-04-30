import type { TimeZone } from "@/apiclient";
import { getTimeInTimezone, getTimezoneUTCString } from "@/utils";

const LocalTime = ({ timezone }: { timezone: TimeZone | "" }) => {
  return (
    <>
      {getTimeInTimezone(new Date(), timezone)} UTC{getTimezoneUTCString(timezone)}
    </>
  );
};

export default LocalTime;
