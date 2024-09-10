import { ContentSection } from "@canonical/maas-react-components";
import { Button, Input, Label, Notification } from "@canonical/react-components";
import { useQueryClient } from "@tanstack/react-query";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

import type { User } from "@/api/client";
import { useCurrentUserQuery, useUpdateCurrentUserMutation } from "@/hooks/react-query";

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
  const updateUser = useUpdateCurrentUserMutation({
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
    updateUser.mutate({ requestBody: { ...userData } });
  };

  return (
    <ContentSection variant="narrow">
      <ContentSection.Title>Personal Details</ContentSection.Title>
      {updateUser.isSuccess && (
        <Notification severity="positive" title="Details Updated">
          Your details were updated successfully
        </Notification>
      )}
      <Formik
        enableReinitialize
        initialValues={initialValues}
        onSubmit={handleSubmit}
        validateOnBlur={false}
        validationSchema={PersonalDetailsUpdateSchema}
      >
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <Form aria-label="update personal details" aria-labelledby={headingId} noValidate>
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
            <Field as={Input} error={touched.full_name && errors.full_name} id={nameId} name="full_name" type="text" />
            <Label className="is-required" htmlFor={emailId}>
              Email Address
            </Label>
            <Field as={Input} error={touched.email && errors.email} id={emailId} name="email" required type="email" />
            <ContentSection.Footer>
              <Button appearance="positive" disabled={!dirty || !isValid || isSubmitting} type="submit">
                Save
              </Button>
            </ContentSection.Footer>
          </Form>
        )}
      </Formik>
    </ContentSection>
  );
};

export default PersonalDetailsUpdate;
