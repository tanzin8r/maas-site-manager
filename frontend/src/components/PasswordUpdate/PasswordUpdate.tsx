import { ContentSection } from "@canonical/maas-react-components";
import { Notification, Button, Input, Label } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Formik, Field } from "formik";
import * as Yup from "yup";

import ErrorMessage from "../ErrorMessage";
import FormikFormContent from "../base/FormikFormContent";

import type { MutationErrorResponse } from "@/api";
import { useChangePassword } from "@/api/query/users";
const initialValues = {
  current_password: "",
  new_password: "",
  confirm_password: "",
};

type PasswordUpdateFormValues = typeof initialValues;
const PasswordUpdateSchema = Yup.object().shape({
  current_password: Yup.string().required("Current password is required"),
  new_password: Yup.string()
    .required("New password is required")
    .min(8, "Password must be at least 8 characters.")
    .max(150, "Password must be 150 characters or less."),
  confirm_password: Yup.string()
    .oneOf([Yup.ref("new_password")], "New passwords must match")
    .required("New password (again) is required"),
});

const PasswordUpdate = () => {
  const headingId = useId();
  const currentPasswordId = useId();
  const newPasswordId = useId();
  const newPasswordConfirmId = useId();
  const updatePassword = useChangePassword();

  const handleSubmit = async (values: PasswordUpdateFormValues, helpers: FormikHelpers<PasswordUpdateFormValues>) => {
    const { current_password, new_password, confirm_password } = values;
    updatePassword.mutate(
      {
        body: {
          current_password,
          new_password,
          confirm_password,
        },
      },
      {
        onSuccess: () => {
          helpers.resetForm();
        },
      },
    );
  };

  return (
    <ContentSection variant="narrow">
      <ContentSection.Title>Password</ContentSection.Title>
      {updatePassword.isSuccess && (
        <Notification severity="positive" title="Password Updated">
          Your password has been updated
        </Notification>
      )}
      {updatePassword.isError && (
        <Notification severity="negative" title="Error while updating password:">
          <ErrorMessage error={{ body: updatePassword.error?.response?.data }} />
        </Notification>
      )}
      <Formik
        initialValues={initialValues}
        onSubmit={handleSubmit}
        validateOnBlur={false}
        validationSchema={PasswordUpdateSchema}
      >
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <FormikFormContent
            aria-label="update password"
            aria-labelledby={headingId}
            errors={[{ body: updatePassword.error?.response?.data } as MutationErrorResponse]}
            noValidate
          >
            <Label htmlFor={currentPasswordId} required>
              Current password
            </Label>
            <Field
              as={Input}
              error={touched.current_password && errors.current_password}
              help="If you can't remember your current password, ask an admin to change your password."
              helpClassName="input-help"
              id={currentPasswordId}
              name="current_password"
              required
              type="password"
            />
            <Label htmlFor={newPasswordId} required>
              New password
            </Label>
            <Field
              as={Input}
              error={touched.new_password && errors.new_password}
              id={newPasswordId}
              name="new_password"
              required
              type="password"
            />
            <Label htmlFor={newPasswordConfirmId} required>
              New password (again)
            </Label>
            <Field
              as={Input}
              error={touched.confirm_password && errors.confirm_password}
              help="Enter the same password as before, for verification"
              helpClassName="input-help"
              id={newPasswordConfirmId}
              name="confirm_password"
              required
              type="password"
            />
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

export default PasswordUpdate;
