const ErrorMessage = ({
  error,
  defaultMessage = "An unknown error has occured",
}: {
  error: unknown;
  defaultMessage?: string;
}) => <>{error instanceof Error ? error.message : typeof error === "string" ? error : defaultMessage}</>;

export default ErrorMessage;
