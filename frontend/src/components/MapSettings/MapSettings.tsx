import { ContentSection } from "@canonical/maas-react-components";
import { ActionButton, Input, Notification, Spinner } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Form, Formik } from "formik";
import useLocalStorageState from "use-local-storage-state";
import * as Yup from "yup";

import ErrorMessage from "../ErrorMessage";

import { useCurrentUserQuery } from "@/hooks/react-query";

type MapSettingsFormValues = {
  acceptedOsmTos: boolean;
};

export type MapSettingsStorageState = {
  [username: string]: boolean;
};

const MapSettingsSchema = Yup.object().shape({
  acceptedOsmTos: Yup.boolean(),
});

const MapSettings = () => {
  const [accepted, setAccepted] = useLocalStorageState<MapSettingsStorageState>("hasAcceptedOsmTos", {
    defaultValue: {},
  });
  const [success, setSuccess] = useState(false);
  const { data: currentUser, isPending, isError, error } = useCurrentUserQuery();

  if (isPending) {
    return <Spinner text="Loading..." />;
  }

  if (isError) {
    return (
      <Notification severity="negative" title="Error while fetching user">
        <ErrorMessage error={error} />
      </Notification>
    );
  }

  const initialValues: MapSettingsFormValues = { acceptedOsmTos: accepted[currentUser.username] };

  const handleSubmit = async (
    values: MapSettingsFormValues,
    { setSubmitting, resetForm }: FormikHelpers<MapSettingsFormValues>,
  ) => {
    setSuccess(false);
    setAccepted({ ...accepted, [currentUser.username]: values.acceptedOsmTos });
    setSubmitting(false);
    setSuccess(true);
    resetForm({ values: { acceptedOsmTos: values.acceptedOsmTos } });
  };

  return (
    <ContentSection variant="narrow">
      <ContentSection.Title>Map</ContentSection.Title>
      <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={MapSettingsSchema}>
        {({ isSubmitting, errors, touched, isValid, dirty, setValues, values }) => (
          <Form aria-label="Map settings">
            <h2 className="p-heading--5 u-no-margin--bottom">OpenStreetMap terms of service</h2>
            <p>
              For the map view on the regions page MAAS Site Manager uses the public OpenStreetMap API. In order to
              enable the map view you must accept the OpenStreetMap terms of service and confirm, that you have accepted
              their fair use policy.
            </p>
            {/*Replaced Field with using its as= component Input directly as per https://github.com/jaredpalmer/formik/issues/4017*/}
            <Input
              checked={values.acceptedOsmTos}
              error={touched.acceptedOsmTos && errors.acceptedOsmTos}
              label="I have read and accept the OpenStreetMap term of service and their fair use policy."
              name="acceptedOsmTos"
              onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                setValues({ acceptedOsmTos: event.target.checked });
              }}
              type="checkbox"
            />
            <ContentSection.Footer>
              <ActionButton
                appearance="positive"
                disabled={!dirty || !isValid || isSubmitting}
                loading={isSubmitting}
                success={success}
                type="submit"
              >
                Save
              </ActionButton>
            </ContentSection.Footer>
          </Form>
        )}
      </Formik>
    </ContentSection>
  );
};

export default MapSettings;
