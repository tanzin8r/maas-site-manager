import { ActionButton, Button, Input, Label, Notification, Spinner } from "@canonical/react-components";
import { Field, Form, Formik } from "formik";
import * as Yup from "yup";

import ErrorMessage from "@/components/ErrorMessage/ErrorMessage";
import { useAppLayoutContext } from "@/context";
import { useRegionDetailsContext } from "@/context/RegionDetailsContext";
import { useSiteQuery } from "@/hooks/react-query";

const baseInitialValues = {
  street: "",
  city: "",
  zip: "",
  coordinates: "",
};

const EditRegionSchema = Yup.object().shape({
  street: Yup.string(),
  city: Yup.string(),
  zip: Yup.string(),
  coordinates: Yup.string()
    .matches(
      /^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$/,
      "Latitude and Longitude input can only contain numerical characters (0-9), a decimal point (.), a comma (,), or a minus (-).",
    )
    .matches(
      /^[-]?([1-8]?\d(\.\d+)?|90(\.0+)?)\s*,\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)$/,
      "Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma (,).",
    ),
});

type RegionFormValues = typeof baseInitialValues;

const EditRegion = () => {
  const headingId = useId();
  const streetId = useId();
  const cityId = useId();
  const zipId = useId();
  const coordinatesId = useId();

  const [initialValues, setInitialValues] = useState<RegionFormValues>(baseInitialValues);
  const { regionId, setRegionId } = useRegionDetailsContext();
  const { setSidebar } = useAppLayoutContext();
  const { data: region, error, isLoading } = useSiteQuery(regionId);

  useEffect(() => {
    if (region) {
      setInitialValues({
        street: region.street,
        city: region.city,
        zip: region.zip,
        coordinates: `${region.latitude}, ${region.longitude}`,
      });
    }
  }, [region]);

  const handleSubmit = async (values: RegionFormValues) => {
    const [latitude, longitude] = values.coordinates.replace(/\s+/g, "").split(",");
    const regionData = {
      street: values.street,
      city: values.city,
      zip: values.zip,
      latitude,
      longitude,
    };
    // eslint-disable-next-line no-console
    console.table(regionData);
    // TODO: Enable mutation here once implemented in backend https://warthogs.atlassian.net/browse/MAASENG-2059
  };

  const resetForm = () => {
    setInitialValues(baseInitialValues);
    setRegionId(null);
    setSidebar(null);
  };

  return (
    <div>
      {!isLoading && region && initialValues !== baseInitialValues ? (
        <>
          <h3 className="p-heading--4 u-no-margin" id={headingId}>
            Edit <strong>{region.name}</strong>
          </h3>
          <p>Data not shown in this form is reported by the MAAS site and can't be edited in Site Manager.</p>
          <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={EditRegionSchema}>
            {({ isSubmitting, errors, touched, isValid, dirty }) => (
              <Form aria-labelledby={headingId}>
                <h4 className="p-heading--5">Geolocation data</h4>
                {/* TODO: Add country input field https://warthogs.atlassian.net/browse/MAASENG-2055 */}
                <Label htmlFor={streetId}>Street</Label>
                <Field as={Input} error={touched.street && errors.street} id={streetId} name="street" type="text" />
                <Label htmlFor={cityId}>City</Label>
                <Field as={Input} error={touched.city && errors.city} id={cityId} name="city" type="text" />
                <Label htmlFor={zipId}>Zip</Label>
                <Field as={Input} error={touched.zip && errors.zip} id={zipId} name="zip" type="text" />
                <Label htmlFor={coordinatesId}>Latitude and Longitude</Label>
                <Field
                  as={Input}
                  className="u-no-margin"
                  error={touched.coordinates && errors.coordinates}
                  help={<small className="u-text--muted">Coordinates need to be a comma-separated pair.</small>}
                  id={coordinatesId}
                  name="coordinates"
                  type="text"
                />
                {/* TODO: Add timezone input field https://warthogs.atlassian.net/browse/MAASENG-2018 */}
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
                    Save
                  </ActionButton>
                </div>
              </Form>
            )}
          </Formik>
        </>
      ) : error ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage error={error} />
        </Notification>
      ) : (
        <Spinner text="Loading..." />
      )}
    </div>
  );
};

export default EditRegion;
