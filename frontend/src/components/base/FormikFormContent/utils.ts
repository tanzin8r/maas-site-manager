import { usePrevious } from "@canonical/react-components";
import { useFormikContext } from "formik";
import { isEqual } from "lodash";

import { type MutationErrorResponse } from "@/api";

export type FieldErrors = {
  [key: string]: string;
};

/**
 * Extracts field-specific error messages from a mutation error response.
 *
 * @param error - The error response object containing details about the mutation error.
 * @returns An object mapping field names to their respective error messages.
 */
export const getFieldErrorsFromErrorResponse = (error: MutationErrorResponse): FieldErrors => {
  let fieldErrors: FieldErrors = {};
  if (error.body.error.details) {
    for (const detail of error.body.error.details) {
      if (detail.field) {
        // Errors for coordinates are seperated into coordinates.latitude and coordinates.longitude,
        // but we only display one coordinates field in the UI, so errors from both need to go here.
        const field = detail.field.includes("coordinates") ? "coordinates" : detail.field;
        if (detail.messages.length > 0) {
          fieldErrors[field] = detail.messages.join(" ");
        } else {
          fieldErrors[field] = "An unknown error occurred when processing this field.";
        }
      }
    }
  }
  return fieldErrors;
};

/**
 * Checks if the given error is a MutationErrorResponse.
 *
 * @param error - The error object to be checked.
 * @returns A boolean indicating whether the error is a MutationErrorResponse.
 */
export const isMutationErrorResponse = (error: unknown): error is MutationErrorResponse => {
  if (typeof error === "object" && !!error && "body" in error) {
    const { body } = error;
    if (typeof body === "object" && !!body && "error" in body) {
      return true;
    }
  }
  return false;
};

/**
 * A hook to handle setting form field errors in Formik based on an array of error responses.
 * The hook runs an effect whenever the `errors` array changes. If the errors have changed and are not null,
 * it iterates over the errors and sets the corresponding field errors in Formik (using Formik's context).
 *
 * @template V - The type of the form values.
 * @param {Array<MutationErrorResponse | null> | undefined} errors - An array of error responses or null.
 * @returns {void}
 */
export const useFormikErrors = <V extends object>(errors: (MutationErrorResponse | null)[] | undefined): void => {
  const { setFieldError } = useFormikContext<V>();

  const previousErrors = usePrevious(errors, false);

  useEffect(() => {
    // only run if errors have changed
    if (!isEqual(errors, previousErrors) && !!errors) {
      for (const error of errors) {
        // skip if error is not MutationErrorResponse
        if (!error || !isMutationErrorResponse(error)) {
          continue;
        }
        const fieldErrors = getFieldErrorsFromErrorResponse(error);
        for (const field in fieldErrors) {
          setFieldError(field, fieldErrors[field]);
        }
      }
    }
  }, [errors, previousErrors, setFieldError]);
};
