import { Input } from "@canonical/react-components";
import { Field, Formik } from "formik";

import FormikFormContent from "./FormikFormContent";

import { ExceptionCode, type MutationErrorResponse } from "@/api";
import { render, screen, waitFor } from "@/utils/test-utils";

const renderForm = ({ apiErrors }: { apiErrors: MutationErrorResponse[] }) => {
  const initialValues = {
    username: "",
    email: "",
  };

  return render(
    <Formik initialValues={initialValues} onSubmit={vi.fn()}>
      {({ errors }) => (
        <FormikFormContent aria-label="Test form" errors={apiErrors}>
          <Field aria-label="Username" as={Input} error={errors.username} name="username" type="text" />
          <Field aria-label="Email" as={Input} error={errors.email} name="email" type="text" />
        </FormikFormContent>
      )}
    </Formik>,
  );
};

it("renders form fields correctly", () => {
  renderForm({ apiErrors: [] });

  expect(screen.getByRole("form", { name: "Test form" })).toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Username" })).toBeInTheDocument();
  expect(screen.getByRole("textbox", { name: "Email" })).toBeInTheDocument();
});

it("displays detailed API errors on the relevant fields", async () => {
  const errorResponse: MutationErrorResponse = {
    body: {
      error: {
        code: ExceptionCode.INVALID_PARAMETERS,
        message: "Validation error",
        details: [
          { field: "email", messages: ["Email is already taken"], reason: "Validation error" },
          { field: "username", messages: ["Username is not creative enough"], reason: "Validation error" },
        ],
      },
    },
  };

  renderForm({ apiErrors: [errorResponse] });

  await waitFor(() => {
    expect(screen.getByRole("textbox", { name: "Username" }).nextElementSibling).toHaveTextContent(
      "Username is not creative enough",
    );
  });

  expect(screen.getByRole("textbox", { name: "Email" }).nextElementSibling).toHaveTextContent("Email is already taken");
});
