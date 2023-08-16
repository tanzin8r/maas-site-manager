import { ActionButton, Button, Input, Label, Notification, Spinner, Select } from "@canonical/react-components";
import { Field, Form, Formik } from "formik";
import en from "i18n-iso-countries/langs/en.json";
import * as Yup from "yup";

import ErrorMessage from "@/components/ErrorMessage/ErrorMessage";
import { useAppLayoutContext } from "@/context";
import type { SiteDetailsContextValue } from "@/context/SiteDetailsContext";
import { useSiteDetailsContext } from "@/context/SiteDetailsContext";
import { useSiteQuery } from "@/hooks/react-query";
import { getCountryName } from "@/utils";

const countryOptions = [
  { value: "", label: "Select country...", disabled: true },
  ...Object.keys(en.countries).map((countryCode) => ({
    value: countryCode,
    label: getCountryName(countryCode),
  })),
] as const;

const baseInitialValues = {
  country: "",
  street: "",
  city: "",
  coordinates: "",
};

const EditSiteSchema = Yup.object().shape({
  street: Yup.string(),
  city: Yup.string(),
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

type SiteFormValues = typeof baseInitialValues;

const EditSiteContent = ({
  siteId,
  setSiteId,
}: {
  siteId: NonNullable<SiteDetailsContextValue["selected"]>;
  setSiteId: NonNullable<SiteDetailsContextValue["setSelected"]>;
}) => {
  const headingId = useId();
  const countryId = useId();
  const streetId = useId();
  const cityId = useId();
  const coordinatesId = useId();

  const [initialValues, setInitialValues] = useState<SiteFormValues>(baseInitialValues);
  const { previousSidebar, setSidebar } = useAppLayoutContext();
  const { data: site, error, isLoading } = useSiteQuery({ id: siteId });

  useEffect(() => {
    if (site) {
      setInitialValues({
        street: site.street ?? "",
        city: site.city ?? "",
        country: site.country ?? "",
        coordinates: `${site.latitude}, ${site.longitude}`,
      });
    }
  }, [site]);

  const handleSubmit = async (values: SiteFormValues) => {
    const [latitude, longitude] = values.coordinates.replace(/\s+/g, "").split(",");
    const siteData = {
      street: values.street,
      city: values.city,
      country: values.country,
      latitude,
      longitude,
    };
    // eslint-disable-next-line no-console
    console.table(siteData);
    // TODO: Enable mutation here once implemented in backend https://warthogs.atlassian.net/browse/MAASENG-2059
    resetForm();
  };

  const resetForm = () => {
    setInitialValues(baseInitialValues);
    if (previousSidebar) {
      setSidebar(previousSidebar);
    } else {
      setSiteId(null);
      setSidebar(null);
    }
  };

  return (
    <div>
      {!isLoading && site && initialValues !== baseInitialValues ? (
        <>
          <h3 className="p-heading--4 u-no-margin" id={headingId}>
            Edit <strong>{site.name}</strong>
          </h3>
          <p>Data not shown in this form is reported by the MAAS site and can't be edited in Site Manager.</p>
          <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={EditSiteSchema}>
            {({ isSubmitting, errors, touched, isValid, dirty }) => (
              <Form aria-labelledby={headingId}>
                <h4 className="p-heading--5">Geolocation data</h4>
                <Label htmlFor={countryId}>Country</Label>
                <Field
                  as={Select}
                  error={touched.country && errors.country}
                  id={countryId}
                  name="country"
                  options={countryOptions}
                />
                <Label htmlFor={streetId}>Street</Label>
                <Field as={Input} error={touched.street && errors.street} id={streetId} name="street" type="text" />
                <Label htmlFor={cityId}>City</Label>
                <Field as={Input} error={touched.city && errors.city} id={cityId} name="city" type="text" />
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

const EditSite = () => {
  const { selected: siteId, setSelected: setSiteId } = useSiteDetailsContext();

  return siteId ? <EditSiteContent setSiteId={setSiteId} siteId={siteId} /> : null;
};

export default EditSite;
