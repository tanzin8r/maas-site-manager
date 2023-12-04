import { useId } from "react";

import { Button, Input, Label, Notification } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Formik, Form } from "formik";
import * as Yup from "yup";

import { humanIntervalToISODuration } from "./utils";

import { useAppLayoutContext } from "@/context";
import { useTokensCreateMutation } from "@/hooks/react-query";

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
  const tokensCreateMutation = useTokensCreateMutation();
  const { setSidebar } = useAppLayoutContext();
  const handleSubmit = async (
    { amount, expires }: TokensCreateFormValues,
    { setSubmitting }: FormikHelpers<TokensCreateFormValues>,
  ) => {
    await tokensCreateMutation.mutateAsync({
      count: Number(amount),
      duration: humanIntervalToISODuration(expires) as string,
    });
    setSubmitting(false);
    setSidebar(null);
  };

  return (
    <div className="tokens-create">
      <h3 className="tokens-create__heading p-heading--4" id={headingId}>
        Generate new enrolment tokens
      </h3>
      {tokensCreateMutation.isError && (
        <Notification severity="negative">There was an error generating the token(s).</Notification>
      )}
      <Formik
        initialValues={initialValues}
        onSubmit={handleSubmit}
        validateOnBlur={false}
        validationSchema={TokensCreateSchema}
      >
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <Form aria-labelledby={headingId} className="tokens-create" noValidate>
            <Label htmlFor={amountId}>Amount of tokens to generate</Label>
            <Field
              as={Input}
              error={touched.amount && errors.amount}
              id={amountId}
              name="amount"
              placeholder="1"
              required
              type="text"
            />
            <Label htmlFor={expiresId}>Expiration time</Label>
            <Field
              as={Input}
              error={touched.expires && errors.expires}
              id={expiresId}
              name="expires"
              placeholder="12 hours"
              required
              type="text"
            />
            <p className="u-text--muted">
              Use this token once to request an enrolment in the specified timeframe. Allowed time units are seconds,
              minutes, hours, days and weeks.
            </p>
            <hr className="tokens-create__separator" />
            <div className="tokens-create__buttons">
              <Button appearance="base" onClick={() => setSidebar(null)} type="button">
                Cancel
              </Button>
              <Button
                appearance="positive"
                disabled={!dirty || !isValid || tokensCreateMutation.isPending || isSubmitting}
                type="submit"
              >
                Generate tokens
              </Button>
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default TokensCreate;
