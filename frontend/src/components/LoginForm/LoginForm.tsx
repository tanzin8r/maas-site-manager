import { useCallback, useEffect } from "react";

import { Notification, Col, Row, Strip, Input, useId, Label, Card, Button } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

import { useAuthContext } from "@/context";
import { useNavigate, useSearchParams } from "@/utils/router";

const initialValues = {
  username: "",
  password: "",
} as const;

type LoginFormValues = typeof initialValues;

const LoginFormSchema = Yup.object().shape({
  username: Yup.string().required("Please enter an email address."),
  password: Yup.string().required("Please enter a password."),
});

const LoginForm = () => {
  const id = useId();
  const headingId = `heading-${id}`;
  const emailId = `username-${id}`;
  const passwordId = `password=${id}`;
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login, isError, failureReason, status } = useAuthContext();
  // TODO: update error response types  https://warthogs.atlassian.net/browse/MAASENG-2082
  /* @ts-ignore-next-line */
  const failureDetails = failureReason?.body?.detail;
  const handleRedirect = useCallback(() => {
    // send user back to the page they tried to visit
    // { replace: true } avoids going back to login page once authenticated
    navigate(searchParams.get("redirectTo") ?? "/sites", { replace: true });
  }, [searchParams, navigate]);

  const handleSubmit = async (
    { username, password }: LoginFormValues,
    { setSubmitting }: FormikHelpers<LoginFormValues>,
  ) => {
    await login({ username, password });
    setSubmitting(false);
  };

  useEffect(() => {
    if (status === "authenticated") {
      handleRedirect();
    }
  }, [handleRedirect, status]);

  return (
    <>
      <Strip>
        {isError ? (
          <Row>
            <Col emptyLarge={4} size={6}>
              <Notification role="alert" severity="negative" title="Error">
                {failureDetails && typeof failureDetails === "string" ? failureDetails : "An unknown error occurred"}
              </Notification>
            </Col>
          </Row>
        ) : null}
        <Row>
          <Col emptyLarge={4} size={6}>
            <Card>
              <h1 className="p-card__title p-heading--3" id={headingId}>
                Login
              </h1>
              <Formik<LoginFormValues>
                initialValues={initialValues}
                onSubmit={handleSubmit}
                validateOnBlur={false}
                validationSchema={LoginFormSchema}
              >
                {({ isSubmitting, errors, touched, isValid, dirty }) => (
                  <Form aria-labelledby={headingId}>
                    <Label htmlFor={emailId}>Email</Label>
                    <Field
                      as={Input}
                      error={touched.username && errors.username}
                      id={emailId}
                      name="username"
                      required
                      type="email"
                    />
                    <Label htmlFor={passwordId}>Password</Label>
                    <Field
                      as={Input}
                      error={touched.password && errors.password}
                      id={passwordId}
                      name="password"
                      required
                      type="password"
                    />
                    <Button appearance="positive" disabled={!dirty || !isValid || isSubmitting} type="submit">
                      Login
                    </Button>
                  </Form>
                )}
              </Formik>
            </Card>
          </Col>
        </Row>
      </Strip>
    </>
  );
};

export default LoginForm;
