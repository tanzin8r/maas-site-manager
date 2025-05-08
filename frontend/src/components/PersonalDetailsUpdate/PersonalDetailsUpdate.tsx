import { ContentSection } from "@canonical/maas-react-components";
import { Button, Input, Label, Notification } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Formik } from "formik";
import * as Yup from "yup";

import type { MutationErrorResponse } from "@/api";
import { useCurrentUser, useEditCurrentUser } from "@/api/query/users";
import type { User } from "@/apiclient";
import ErrorMessage from "@/components/ErrorMessage";
import FormikFormContent from "@/components/base/FormikFormContent";

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
  const { data, isSuccess } = useCurrentUser();
  const updateUser = useEditCurrentUser();

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
    const { full_name, email, username } = userData;
    updateUser.mutate({ body: { full_name, username, email } });
  };

  return (
    <ContentSection variant="narrow">
      <ContentSection.Title>Personal Details</ContentSection.Title>
      {updateUser.isSuccess && (
        <Notification severity="positive" title="Details Updated">
          Your details were updated successfully
        </Notification>
      )}
      {updateUser.isError && (
        <Notification severity="negative" title="Error while updating details">
          <ErrorMessage error={{ body: updateUser.error.response?.data }} />
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
          <FormikFormContent
            aria-label="update personal details"
            aria-labelledby={headingId}
            errors={[{ body: updateUser.error?.response?.data } as MutationErrorResponse]}
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
          </FormikFormContent>
        )}
      </Formik>
    </ContentSection>
  );
};

export default PersonalDetailsUpdate;
