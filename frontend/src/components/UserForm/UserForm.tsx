import { ActionButton, Button, CheckboxInput, Input, Label, Notification, Spinner } from "@canonical/react-components";
import { useQueryClient } from "@tanstack/react-query";
import { Field, Form, Formik } from "formik";
import { isEqual } from "lodash";
import * as Yup from "yup";

import { useAppLayoutContext } from "@/context";
import { useUserSelectionContext } from "@/context/UserSelectionContext";
import { useUpdateUserMutation, useUserQuery } from "@/hooks/react-query";

const baseInitialValues = {
  username: "",
  full_name: "",
  email: "",
  is_admin: false,
  password: "",
  confirm_password: "",
};

type UserFormValues = typeof baseInitialValues;

const baseSchemaFields = {
  email: Yup.string().email("Must be a valid email address").required("Email is required"),
  full_name: Yup.string(),
  is_admin: Yup.boolean(),
  username: Yup.string()
    .max(150, "Username must be 150 characters or less")
    .matches(/^[a-zA-Z0-9@.+-_]*$/, "Usernames must contain letters, digits and @/./+/-/_ only")
    .required("Username is required"),
};

const fullSchemaFields = {
  ...baseSchemaFields,
  password: Yup.string()
    .min(8, "Password must be at least 8 characters.")
    .max(100, "Password must be 100 characters or less"),
  confirm_password: Yup.string().oneOf(
    [Yup.ref("password")],
    "New passwords do not match. Please ensure the new passwords are the same.",
  ),
};

const NoPasswordUserSchema = Yup.object().shape(baseSchemaFields);

const EditUserSchema = Yup.object().shape(fullSchemaFields);

const AddUserSchema = Yup.object().shape({
  ...fullSchemaFields,
  password: fullSchemaFields.password.required("Password is required"),
  confirm_password: fullSchemaFields.confirm_password.required("Password is required"),
});

const UserForm = ({ type }: { type: "add" | "edit" }) => {
  // Field label IDs
  const headingId = useId();
  const usernameId = useId();
  const fullNameId = useId();
  const emailId = useId();
  const passwordId = useId();
  const confirmPasswordId = useId();

  const [initialValues, setInitialValues] = useState<UserFormValues>(baseInitialValues);

  const { setSidebar } = useAppLayoutContext();
  const queryClient = useQueryClient();
  const { selectedUserId, setSelectedUserId } = useUserSelectionContext();
  const { data: user, error, isLoading } = useUserQuery({ id: selectedUserId, enabled: type === "edit" });

  const resetForm = () => {
    setSidebar(null);
    setSelectedUserId(null);
    setInitialValues(baseInitialValues);
  };

  const updateUser = useUpdateUserMutation({
    onSuccess(data) {
      queryClient.setQueryData([user?.username ?? "user"], () => data);
      resetForm();
    },
  });

  useEffect(() => {
    if (type === "edit" && user) {
      setInitialValues({
        username: user.username,
        full_name: user.full_name ? user.full_name : "",
        email: user.email,
        is_admin: user.is_admin,
        password: "",
        confirm_password: "",
      });
    }
  }, [type, user]);

  const handleSubmit = async (values: UserFormValues) => {
    const userData = {
      email: values.email,
      username: values.username,
      is_admin: values.is_admin,
      full_name: values.full_name,
    };
    if (type === "edit") {
      if (!values.password) {
        await NoPasswordUserSchema.validate(values);
        updateUser.mutate({ userId: user!.id, userData });
      } else {
        await AddUserSchema.validate(values);
        updateUser.mutate({
          userId: user!.id,
          userData: { ...userData, password: values.password, confirm_password: values.confirm_password },
        });
      }
    } // TODO: Implement functionality for adding users https://warthogs.atlassian.net/browse/MAASENG-1870
  };

  return (
    <div>
      <h3 className="p-heading--4" id={headingId}>
        {type === "add" ? "Add user" : `Edit ${user ? user.username : ""}`}
      </h3>
      {error ? (
        <Notification severity="negative" title="Error while fetching user">
          {error instanceof Error ? error.message : "An unknown error has occurred."}
        </Notification>
      ) : null}
      {updateUser.isError && (
        <Notification severity="negative" title="Error while editing user">
          {updateUser.error instanceof Error ? updateUser.error.message : "An unknown error has occurred."}
        </Notification>
      )}
      {type === "edit" && (isEqual(initialValues, baseInitialValues) || isLoading) ? (
        <Spinner text="Loading..." />
      ) : (
        <Formik
          initialValues={initialValues}
          onSubmit={handleSubmit}
          validationSchema={type === "add" ? AddUserSchema : EditUserSchema}
        >
          {({ isSubmitting, errors, touched, isValid, dirty, values }) => (
            <Form aria-labelledby={headingId}>
              <h4 className="p-heading--5">Personal details</h4>
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
              <Label htmlFor={fullNameId}>Full name (optional)</Label>
              <Field
                as={Input}
                error={touched.full_name && errors.full_name}
                id={fullNameId}
                name="full_name"
                type="text"
              />
              <Label className="is-required" htmlFor={emailId}>
                Email address
              </Label>
              <Field as={Input} error={touched.email && errors.email} id={emailId} name="email" required type="email" />
              <Field
                as={CheckboxInput}
                error={touched.is_admin && errors.is_admin}
                label="MAAS Site Manager administrator"
                name="is_admin"
                type="checkbox"
              />
              <hr />
              <h4 className="p-heading--5">{type === "edit" ? "Change " : null}Password</h4>
              <Label className={type === "add" ? "is-required" : null} htmlFor={passwordId}>
                Password
              </Label>
              <Field
                as={Input}
                error={touched.password && errors.password}
                id={passwordId}
                name="password"
                required={type === "add"}
                type="password"
              />
              <Label className={type === "add" ? "is-required" : null} htmlFor={confirmPasswordId}>
                Password (again)
              </Label>
              <Field
                as={Input}
                error={errors.confirm_password}
                id={confirmPasswordId}
                name="confirm_password"
                required={type === "add" || values.password !== ""}
                type="password"
              />
              <p className="u-text--muted">Enter the same password as before, for verification</p>

              <hr />
              <div className="u-flex u-flex--justify-end u-padding-top--medium">
                <Button appearance="base" onClick={resetForm} type="button">
                  Cancel
                </Button>
                <ActionButton
                  appearance="positive"
                  disabled={!dirty || !isValid || isSubmitting}
                  loading={isSubmitting}
                  type="submit"
                >
                  {type === "add" ? "Add user" : "Save"}
                </ActionButton>
              </div>
            </Form>
          )}
        </Formik>
      )}
    </div>
  );
};

export default UserForm;
