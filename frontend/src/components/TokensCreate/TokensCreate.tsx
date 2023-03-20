import { useId } from "react";

import { Button, Input, Label, Notification } from "@canonical/react-components";
import { Field, Formik, Form } from "formik";
import { Link, useNavigate } from "react-router-dom";
import * as Yup from "yup";

import "./TokensCreate.scss";
import { humanIntervalToISODuration } from "./utils";

import { useTokensMutation } from "@/hooks/api";

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
  const navigate = useNavigate();
  const tokensMutation = useTokensMutation();
  const handleSubmit = async (
    { amount, expires }: TokensCreateFormValues,
    { setSubmitting }: { setSubmitting: (isSubmitting: boolean) => void },
  ) => {
    await tokensMutation.mutateAsync({
      amount: Number(amount),
      expires: humanIntervalToISODuration(expires) as string,
    });
    // TODO: update the tokens list once fetching tokens from API is implemented
    // https://warthogs.atlassian.net/browse/MAASENG-1474
    setSubmitting(false);
    navigate("/tokens", { state: { sidebar: false } });
  };

  return (
    <div className="tokens-create">
      <h3 className="tokens-create__heading p-heading--4" id={headingId}>
        Generate new enrollment tokens
      </h3>
      {tokensMutation.isError && (
        <Notification severity="negative">There was an error generating the token(s).</Notification>
      )}
      <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={TokensCreateSchema}>
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <Form aria-labelledby={headingId} className="tokens-create" noValidate>
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
              Use this token once to request an enrolment in the specified timeframe. Allowed time units are seconds,
              minutes, hours, days and weeks.
            </p>
            <hr className="tokens-create__separator" />
            <div className="tokens-create__buttons">
              <Link className="p-button" role="button" state={{ sidebar: false }} to="tokens">
                Cancel
              </Link>
              <Button
                appearance="positive"
                disabled={!dirty || !isValid || tokensMutation.isLoading || isSubmitting}
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
