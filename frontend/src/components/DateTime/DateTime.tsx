import { withErrorBoundary } from "react-error-boundary";

import { formatUTCDateString } from "@/utils";

const DateTime = ({ value }: { value: string }) => <time dateTime={value}>{formatUTCDateString(value)}</time>;

const DateTimeWithErrorBoundary = withErrorBoundary(DateTime, {
  fallback: <div>Invalid time value</div>,
});

export default DateTimeWithErrorBoundary;
