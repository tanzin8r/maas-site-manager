import { ContentSection, FormSection } from "@canonical/maas-react-components";
import { Button, Input } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Formik, Form, Field } from "formik";

import type { TSettingsPatchRequest } from "@/api";
import { useAppLayoutContext } from "@/context";
import { useSettingsQuery, useUpdateSettingsMutation } from "@/hooks/react-query";

type FormValues = Pick<TSettingsPatchRequest, "images_connect_to_maas">;

const formKeys: Record<keyof FormValues, keyof FormValues> = {
  images_connect_to_maas: "images_connect_to_maas",
} as const;

const MaasImages = () => {
  const titleId = useId();
  const { setSidebar } = useAppLayoutContext();
  const { data, isPending } = useSettingsQuery();
  const settingsMutation = useUpdateSettingsMutation();
  const initialValues: FormValues = {
    [formKeys.images_connect_to_maas]: data ? data[formKeys.images_connect_to_maas] : false,
  };

  const handleSubmit = async (values: FormValues, { resetForm, setSubmitting }: FormikHelpers<FormValues>) => {
    // TODO: integrate with APIs and adjust the logic https://warthogs.atlassian.net/browse/MAASENG-2601
    setSidebar("deleteOrKeepImages");
    await settingsMutation.mutate(values);
    setSubmitting(false);
    resetForm({ values });
  };

  return (
    <ContentSection variant="narrow">
      <ContentSection.Title id={titleId}>maas.io</ContentSection.Title>
      <Formik enableReinitialize initialValues={initialValues} onSubmit={handleSubmit}>
        {({ isSubmitting, errors, touched, isValid, dirty }) => (
          <Form aria-labelledby={titleId}>
            <FormSection>
              <FormSection.Description>
                You can choose to connect to the maas.io image server and download images provided by the MAAS team. The
                downloaded images will be periodically updated to the latest version from maas.io.
              </FormSection.Description>
              <FormSection.Content>
                <Field
                  as={Input}
                  disabled={isPending}
                  error={touched[formKeys.images_connect_to_maas] && errors[formKeys.images_connect_to_maas]}
                  label="Connect to maas.io and keep selected images up to date."
                  name={formKeys.images_connect_to_maas}
                  type="checkbox"
                />
              </FormSection.Content>
            </FormSection>
            <ContentSection.Footer>
              <Button appearance="positive" disabled={!dirty || !isValid || isSubmitting || isPending} type="submit">
                Save
              </Button>
            </ContentSection.Footer>
          </Form>
        )}
      </Formik>
    </ContentSection>
  );
};

export default MaasImages;
