import { Col, Row, Strip, Input, useId, Label, Card, Button } from "@canonical/react-components";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

const initialValues = {
  username: "",
  password: "",
};

type LoginFormValues = typeof initialValues;

const LoginFormSchema = Yup.object().shape({
  username: Yup.string().required("Please enter a username."),
  password: Yup.string().required("Please enter a password."),
});

const LoginForm = () => {
  const id = useId();
  const headingId = `heading-${id}`;
  const usernameId = `username-${id}`;
  const passwordId = `password=${id}`;

  const handleSubmit = (values: LoginFormValues) => {
    // 1. send values to backend
    // 2. if error, return error and display
    // 3. if all good, set cookie and navigate to /sites
  };

  return (
    <Strip>
      <Row>
        <Col emptyLarge={4} size={6}>
          <Card>
            <h1 className="p-card__title p-heading--3" id={headingId}>
              Login
            </h1>
            <Formik<LoginFormValues>
              initialValues={initialValues}
              onSubmit={handleSubmit}
              validationSchema={LoginFormSchema}
            >
              {({ isSubmitting, errors, touched, isValid, dirty }) => (
                <Form aria-labelledby={headingId}>
                  <Label htmlFor={usernameId}>Username</Label>
                  <Field
                    as={Input}
                    error={touched.username && errors.username}
                    id={usernameId}
                    name="username"
                    required
                    type="text"
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
  );
};

export default LoginForm;
