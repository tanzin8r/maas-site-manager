import { useEffect } from "react";

import { Button, Icon, Input, useId } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import pluralize from "pluralize";
import * as Yup from "yup";

import { useAppLayoutContext, useRowSelectionContext } from "@/context";
import { useDeleteSitesMutation, useSiteQuery } from "@/hooks/react-query";

const initialValues = {
  confirmText: "",
};

type RemoveSitesFormValues = typeof initialValues;

const RemoveSitesFormSchema = Yup.object().shape({
  confirmText: Yup.string()
    .required()
    .when("$expectedConfirmTextValue", (type, schema) => {
      return schema.equals(type);
    }),
});

const createHandleValidate =
  ({ expectedConfirmTextValue }: { expectedConfirmTextValue: string }) =>
  async (values: RemoveSitesFormValues) => {
    let errors = {};
    await RemoveSitesFormSchema.validate(values, { context: { expectedConfirmTextValue } }).catch(() => {
      errors = { confirmText: `Confirmation string is not correct. Expected ${expectedConfirmTextValue}` };
    });
    return errors;
  };

const RemoveSites = () => {
  const { rowSelection, setRowSelection } = useRowSelectionContext("sites");
  const { previousSidebar, setSidebar } = useAppLayoutContext();
  const deleteSitesMutation = useDeleteSitesMutation();
  const sitesCount = rowSelection && Object.keys(rowSelection).length;
  const id = useId();
  const confirmTextId = `confirm-text-${id}`;
  const headingId = `heading-${id}`;
  const { data } = useSiteQuery({ id: Number(Object.keys(rowSelection)?.[0]) });
  const siteName = data?.name;
  const sitesCountText = sitesCount === 1 ? siteName : pluralize("sites", sitesCount || 0, !!sitesCount);
  const expectedConfirmTextValue = `remove ${sitesCountText}`;
  const handleSubmit = (_values: RemoveSitesFormValues, { setSubmitting }: FormikHelpers<RemoveSitesFormValues>) => {
    const selectedIds = Object.keys(rowSelection).map((id) => Number(id));
    deleteSitesMutation.mutate(selectedIds, {
      onSuccess() {
        setSubmitting(false);
        setSidebar(null);
        setRowSelection({});
      },
    });
  };

  // close the sidebar when there are no sites selected
  useEffect(() => {
    if (!sitesCount) {
      setSidebar(null);
    }
  }, [sitesCount, setSidebar]);

  return (
    <Formik<RemoveSitesFormValues>
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validate={createHandleValidate({ expectedConfirmTextValue })}
    >
      {({ isSubmitting, errors, touched, dirty, submitCount }) => (
        <Form aria-labelledby={headingId} className="tokens-create" noValidate>
          <div className="tokens-create">
            <h3 className="tokens-create__heading p-heading--4" id={headingId}>
              Remove <strong> {sitesCountText}</strong> from Site Manager
            </h3>
            <p>
              The deletion of data is irreversible. You can re-enrol the MAAS {pluralize("sites", sitesCount)} again
              through the enrolment process.
            </p>
            <p id={confirmTextId}>
              Type <strong>remove {sitesCountText}</strong> to confirm.
            </p>
            <Field
              aria-labelledby={confirmTextId}
              as={Input}
              error={submitCount > 0 && touched.confirmText && errors.confirmText}
              name="confirmText"
              placeholder={`remove ${sitesCountText}`}
              type="text"
            />
            <Button
              appearance="base"
              onClick={() => {
                if (previousSidebar) {
                  setSidebar(previousSidebar);
                } else {
                  setSidebar(null);
                }
              }}
              type="button"
            >
              Cancel
            </Button>
            <Button appearance="negative" disabled={!dirty || isSubmitting} type="submit">
              <Icon light name="delete" /> Remove
            </Button>
          </div>
        </Form>
      )}
    </Formik>
  );
};

export default RemoveSites;
