import { ExternalLink } from "@canonical/maas-react-components";
import { Accordion, ActionButton, Button, Input, Label, Spinner, Notification } from "@canonical/react-components";
import type { FormikErrors } from "formik";
import { Field, Form, Formik, useFormikContext } from "formik";
import * as Yup from "yup";

import type { Site } from "@/api";
import { coordinateSchema } from "@/components/EditSite/constants";
import ErrorMessage from "@/components/ErrorMessage/ErrorMessage";
import { useAppLayoutContext } from "@/context";
import { useSitesQuery, useUpdateSitesCoordinatesMutation } from "@/hooks/react-query";

import "./_SitesMissingData.scss";

type SitesMissingDataValues = {
  sitesCoordinates: { id: Site["id"]; coordinates: string }[];
};

const SitesMissingDataSchema = Yup.object().shape({
  sitesCoordinates: Yup.array().of(Yup.object().shape({ id: Yup.number(), coordinates: coordinateSchema })),
});

const SiteMissingDataField = ({ site, index }: { site: Site; index: number }) => {
  const fieldId = useId();
  const { touched, errors } = useFormikContext<SitesMissingDataValues>();

  const fieldErrors = errors.sitesCoordinates?.[index] as FormikErrors<
    SitesMissingDataValues["sitesCoordinates"][number]
  >;

  return (
    <span>
      <hr />
      <Accordion
        sections={[
          {
            content: (
              <>
                <Label>Latitude and Longitude</Label>
                <Field
                  as={Input}
                  error={touched.sitesCoordinates?.[index]?.coordinates && fieldErrors?.coordinates}
                  help="Coordinates need to be a comma-separated pair."
                  id={fieldId}
                  name={`sitesCoordinates[${index}].coordinates`}
                  type="text"
                />
              </>
            ),
            title: (
              <>
                <span>
                  {site.name}
                  <br />
                  {site.url && (
                    <ExternalLink className="sites-missing-data__link" to={site.url}>
                      {site.url}
                    </ExternalLink>
                  )}
                </span>
              </>
            ),
          },
        ]}
      />
    </span>
  );
};

const SitesMissingData = () => {
  const headingId = useId();
  const { setSidebar } = useAppLayoutContext();
  const updateSites = useUpdateSitesCoordinatesMutation({
    onSuccess: () => setSidebar(null),
  });

  const handleSubmit = (values: SitesMissingDataValues) => {
    const { sitesCoordinates } = values;

    // Filter out sites with no coordinates - user doesn't have to add coords for every site
    const filteredValues = sitesCoordinates.filter(({ coordinates }) => coordinates);

    const toSubmit = filteredValues.map(({ id, coordinates }) => ({
      id,
      coordinates: coordinates
        .replace(/\s+/g, "")
        .split(",")
        .map((coordinate) => Number(coordinate)),
    }));

    updateSites.mutate(toSubmit);
  };

  const { data, error, isPending } = useSitesQuery({ missingCoordinates: true, page: 1, size: 20 });

  const sites = data?.items;

  if (isPending) {
    return <Spinner text="Loading..." />;
  }

  if (error) {
    return (
      <Notification severity="negative" title="Error">
        <ErrorMessage error={error} />
      </Notification>
    );
  }

  if (!sites) {
    return null;
  }

  const initialValues: SitesMissingDataValues = {
    sitesCoordinates: sites.map((site) => ({ id: site.id, coordinates: "" })),
  };

  return (
    <div className="sites-missing-data">
      <h3 className="p-heading--4 u-no-margin" id={headingId}>
        Sites with missing data
      </h3>
      <p>
        The following sites have missing latitude and longitude data and are therefore not shown on the map. Add
        latitude and longitude data to the sites in order for them to show up on the map.
        <br />
        {/* TODO: Enable the link below once we have filtering on the sites list https://warthogs.atlassian.net/browse/MAASENG-3442 */}
        {/* <Link to="/sites/list?missing_coordinates=true">Show missing MAAS sites in table view</Link> */}
      </p>
      <strong className="u-uppercase p-text--small">
        Name
        <br />
        URL
      </strong>
      <Formik initialValues={initialValues} onSubmit={handleSubmit} validationSchema={SitesMissingDataSchema}>
        {({ dirty, isValid, isSubmitting, resetForm }) => (
          <Form aria-labelledby={headingId}>
            {sites.map((site, index) => (
              <SiteMissingDataField index={index} key={site.id} site={site} />
            ))}
            <div className="sites-missing-data__form-buttons-wrapper">
              <hr />
              <div className="sites-missing-data__form-buttons">
                <Button
                  appearance="base"
                  onClick={() => {
                    resetForm();
                    setSidebar(null);
                  }}
                  type="button"
                >
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
            </div>
          </Form>
        )}
      </Formik>
    </div>
  );
};

export default SitesMissingData;
