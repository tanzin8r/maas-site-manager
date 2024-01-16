import { ContentSection } from "@canonical/maas-react-components";
import { Row, Col, CheckboxInput, ActionButton } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";
import useLocalStorageState from "use-local-storage-state";
import * as Yup from "yup";

type MapSettingsFormValues = {
  acceptedOsmTos: boolean;
};

const MapSettingsSchema = Yup.object().shape({
  acceptedOsmTos: Yup.boolean(),
});

const MapSettings = () => {
  const [accepted, setAccepted] = useLocalStorageState("hasAcceptedOsmTos", { defaultValue: false });
  const [success, setSuccess] = useState(false);
  const initialValues: MapSettingsFormValues = { acceptedOsmTos: accepted };

  const handleSubmit = async (
    values: MapSettingsFormValues,
    { setSubmitting, resetForm }: FormikHelpers<MapSettingsFormValues>,
  ) => {
    setSuccess(false);
    setAccepted(values.acceptedOsmTos);
    setSubmitting(false);
    setSuccess(true);
    resetForm({ values: { acceptedOsmTos: values.acceptedOsmTos } });
  };

  return (
    <ContentSection>
      <Row>
        <Col size={6}>
          <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={MapSettingsSchema}>
            {({ isSubmitting, errors, touched, isValid, dirty }) => (
              <Form aria-label="Map settings">
                <h2 className="p-heading--5 u-no-margin--bottom">OpenStreetMap terms of service</h2>
                <p>
                  For the map view on the regions page MAAS Site Manager uses the public OpenStreetMap API. In order to
                  enable the map view you must accept the OpenStreetMap terms of service and confirm, that you have
                  accepted their fair use policy.
                </p>
                <Field
                  as={CheckboxInput}
                  error={touched.acceptedOsmTos && errors.acceptedOsmTos}
                  label="I have read and accept the OpenStreetMap term of service and their fair use policy."
                  name="acceptedOsmTos"
                  type="checkbox"
                />
                <ActionButton
                  appearance="positive"
                  disabled={!dirty || !isValid || isSubmitting}
                  loading={isSubmitting}
                  success={success}
                  type="submit"
                >
                  Save
                </ActionButton>
              </Form>
            )}
          </Formik>
        </Col>
      </Row>
    </ContentSection>
  );
};

export default MapSettings;
