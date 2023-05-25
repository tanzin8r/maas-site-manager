import { useEffect } from "react";

import { Button, Icon, Input, useId } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import pluralize from "pluralize";
import * as Yup from "yup";

import { useAppContext, useRowSelectionContext } from "@/context";
import { useSiteQueryData } from "@/hooks/react-query";

const initialValues = {
  confirmText: "",
};

type RemoveRegionsFormValues = typeof initialValues;

const RemoveRegionsFormSchema = Yup.object().shape({
  confirmText: Yup.string()
    .required()
    .when("$expectedConfirmTextValue", (type, schema) => {
      return schema.equals(type);
    }),
});

const createHandleValidate =
  ({ expectedConfirmTextValue }: { expectedConfirmTextValue: string }) =>
  async (values: RemoveRegionsFormValues) => {
    let errors = {};
    await RemoveRegionsFormSchema.validate(values, { context: { expectedConfirmTextValue } }).catch(() => {
      errors = { confirmText: `Confirmation string is not correct. Expected ${expectedConfirmTextValue}` };
    });
    return errors;
  };

const RemoveRegions = () => {
  const { rowSelection } = useRowSelectionContext("sites");
  const { setSidebar } = useAppContext();
  const regionsCount = rowSelection && Object.keys(rowSelection).length;
  const id = useId();
  const confirmTextId = `confirm-text-${id}`;
  const headingId = `heading-${id}`;
  const site = useSiteQueryData(Object.keys(rowSelection)?.[0]);
  const regionName = site?.name;
  const regionsCountText = regionsCount === 1 ? regionName : pluralize("regions", regionsCount || 0, !!regionsCount);
  const expectedConfirmTextValue = `remove ${regionsCountText}`;
  const handleSubmit = (
    _values: RemoveRegionsFormValues,
    { setSubmitting }: FormikHelpers<RemoveRegionsFormValues>,
  ) => {
    setSubmitting(false);
    setSidebar(null);
    // TODO: integrate with delete regions endpoint
  };

  // close the sidebar when there are no regions selected
  useEffect(() => {
    if (!regionsCount) {
      setSidebar(null);
    }
  }, [regionsCount, setSidebar]);

  return (
    <Formik<RemoveRegionsFormValues>
      initialValues={initialValues}
      onSubmit={handleSubmit}
      validate={createHandleValidate({ expectedConfirmTextValue })}
    >
      {({ isSubmitting, errors, touched, dirty, submitCount }) => (
        <Form aria-labelledby={headingId} className="tokens-create" noValidate>
          <div className="tokens-create">
            <h3 className="tokens-create__heading p-heading--4" id={headingId}>
              Remove <strong> {regionsCountText}</strong> from Site Manager
            </h3>
            <p>
              The deletion of data is irreversible. You can re-enrol the MAAS region again through the enrolment
              process.
            </p>
            <p id={confirmTextId}>
              Type <strong>remove {regionsCountText}</strong> to confirm.
            </p>
            <Field
              aria-labelledby={confirmTextId}
              as={Input}
              error={submitCount > 0 && touched.confirmText && errors.confirmText}
              name="confirmText"
              placeholder={`remove ${regionsCountText}`}
              type="text"
            />
            <Button appearance="base" onClick={() => setSidebar(null)} type="button">
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

export default RemoveRegions;
