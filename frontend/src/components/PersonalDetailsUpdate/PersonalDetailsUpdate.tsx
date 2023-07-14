import { Button, Col, Input, Label, Notification, Row } from "@canonical/react-components";
import { useQueryClient } from "@tanstack/react-query";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

import type { User } from "@/api/types";
import { useCurrentUserQuery, useUpdateUserMutation } from "@/hooks/react-query";

type PersonalDetailsUpdateFormValues = Pick<User, "email" | "full_name" | "username">;
const PersonalDetailsUpdateSchema = Yup.object().shape({
  username: Yup.string().required("Username is required"),
  full_name: Yup.string(),
  email: Yup.string().email("Email address is invalid").required("Email address is required"),
});

const PersonalDetailsUpdate = () => {
  const headingId = useId();
  const nameId = useId();
  const emailId = useId();
  const usernameId = useId();
  const [initialValues, setInitialValues] = useState<PersonalDetailsUpdateFormValues>({
    username: "",
    full_name: "",
    email: "",
  });
  const queryClient = useQueryClient();
  const { data, isSuccess } = useCurrentUserQuery();
  const updateUser = useUpdateUserMutation({
    onSuccess(data) {
      queryClient.setQueryData(["me"], () => data);
    },
  });

  useEffect(() => {
    if (isSuccess) {
      setInitialValues({
        username: data.username,
        full_name: data.full_name,
        email: data.email,
      });
    }
  }, [isSuccess, data]);

  const handleSubmit = async (
    userData: PersonalDetailsUpdateFormValues,
    { setSubmitting: _ }: FormikHelpers<PersonalDetailsUpdateFormValues>,
  ) => {
    updateUser.mutate({ userId: data!.id, userData });
  };

  return (
    <Row>
      {updateUser.isSuccess && (
        <Col size={12}>
          <Notification severity="positive" title="Details Updated">
            Your details were updated successfully
          </Notification>
        </Col>
      )}
      <Col size={6}>
        <Formik
          enableReinitialize
          initialValues={initialValues}
          onSubmit={handleSubmit}
          validateOnBlur={false}
          validationSchema={PersonalDetailsUpdateSchema}
        >
          {({ isSubmitting, errors, touched, isValid, dirty }) => (
            <Form
              aria-label="update personal details"
              aria-labelledby={headingId}
              className="personal-details-update-form"
              noValidate
            >
              <Label className="is-required" htmlFor={usernameId}>
                Username
              </Label>
              <Field
                as={Input}
                error={touched.username && errors.username}
                id={usernameId}
                name="username"
                required
                type="text"
              />
              <Label className="" htmlFor={nameId}>
                Full name (optional)
              </Label>
              <Field
                as={Input}
                error={touched.full_name && errors.full_name}
                id={nameId}
                name="full_name"
                type="text"
              />
              <Label className="is-required" htmlFor={emailId}>
                Email Address
              </Label>
              <Field as={Input} error={touched.email && errors.email} id={emailId} name="email" required type="email" />
              <Button appearance="positive" disabled={!dirty || !isValid || isSubmitting} type="submit">
                Save
              </Button>
            </Form>
          )}
        </Formik>
      </Col>
    </Row>
  );
};

export default PersonalDetailsUpdate;
