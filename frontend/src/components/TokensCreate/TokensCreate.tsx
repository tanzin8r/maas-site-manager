import { useId } from "react";

import { Button, Input, Label, Notification } from "@canonical/react-components";
import { useMutation } from "@tanstack/react-query";
import { Field, Formik, Form } from "formik";
import * as Yup from "yup";

import { humanIntervalToISODuration } from "./utils";

import { postTokens } from "@/api/handlers";

const initialValues = {
  amount: "",
  expires: "",
};

type TokensCreateFormValues = typeof initialValues;

const TokensCreateSchema = Yup.object().shape({
  amount: Yup.number().positive().required("Please enter a valid number"),
  expires: Yup.string()
    .matches(
      /^((\d)+ ?(minute|hour|day|week|month|year)(s)? ?(and)? ?)+$/,
      "Time unit must be a `string` type with a value of weeks, days, hours, and/or minutes.",
    )
    .test("Please enter a valid time unit", function (value) {
      if (!value) {
        return false;
      }
      try {
        return !!humanIntervalToISODuration(value);
      } catch (error) {
        return false;
      }
    })
    .required("Please enter a valid time unit"),
});

const TokensCreate = () => {
  const headingId = useId();
  const expiresId = useId();
  const amountId = useId();
  const mutation = useMutation(postTokens);
  const handleSubmit = async (
    { amount, expires }: TokensCreateFormValues,
    { setSubmitting }: { setSubmitting: (isSubmitting: boolean) => void },
  ) => {
    await mutation.mutateAsync({ amount: Number(amount), expires: humanIntervalToISODuration(expires) as string });
    // TODO: update the tokens list once fetching tokens from API is implemented
    // https://warthogs.atlassian.net/browse/MAASENG-1474
    setSubmitting(false);
  };

  return (
    <div>
      <h3 id={headingId}>Generate new enrollment tokens</h3>
      {mutation.isError && <Notification severity="negative">There was an error generating the token(s).</Notification>}
      <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={TokensCreateSchema}>
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <Form aria-labelledby={headingId} noValidate>
            <Label htmlFor={amountId}>Amount of tokens to generate</Label>
            <Field
              as={Input}
              error={touched.amount && errors.amount}
              id={amountId}
              name="amount"
              required
              type="text"
            />
            <Label htmlFor={expiresId}>Expiration time</Label>
            <Field
              as={Input}
              error={touched.expires && errors.expires}
              id={expiresId}
              name="expires"
              required
              type="text"
            />
            <p className="u-text--muted">
              Use this token once to request an enrolment in the specified timeframe. <br />
              Allowed time units are seconds, minutes, hours, days and weeks.
            </p>
            <Button type="button">Cancel</Button>
            <Button
              appearance="positive"
              disabled={!dirty || !isValid || mutation.isLoading || isSubmitting}
              type="submit"
            >
              Generate tokens
            </Button>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default TokensCreate;
