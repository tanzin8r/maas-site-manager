import type { MultiSelectItem } from "@canonical/maas-react-components";
import { ContentSection, ExternalLink, MultiSelect } from "@canonical/maas-react-components";
import { ActionButton, Button, Spinner, Notification } from "@canonical/react-components";
import type { FormikHelpers } from "formik";
import { Field, Form, Formik } from "formik";

import ErrorMessage from "../ErrorMessage";

import type { UpstreamImage } from "@/api";
import { useAppLayoutContext } from "@/context";
import {
  useSelectUpstreamImagesMutation,
  useUpstreamImageSourceQuery,
  useUpstreamImagesQuery,
} from "@/hooks/react-query";

type GroupedImages = {
  [key: string]: ReleasesWithArches;
};

export type ReleasesWithArches = {
  [key: string]: MultiSelectItem[];
};

type ImagesByName = { [key: string]: UpstreamImage[] };

const groupImagesByName = (images: UpstreamImage[]) => {
  let imagesByName: ImagesByName = {};

  images.forEach((image) => {
    if (!!imagesByName[image.codename]) {
      imagesByName[image.codename].push(image);
    } else {
      imagesByName[image.codename] = [image];
    }
  });

  return imagesByName;
};

const groupArchesByRelease = (images: ImagesByName) => {
  let groupedImages: GroupedImages = {};

  Object.keys(images).forEach((distro) => {
    if (!groupedImages[distro]) {
      groupedImages[distro] = {};
    }
    images[distro].forEach((image) => {
      if (!groupedImages[distro][image.release]) {
        groupedImages[distro][image.release] = [{ label: image.arch, value: image.id }];
      } else {
        groupedImages[distro][image.release].push({ label: image.arch, value: image.id });
      }
    });
  });

  return groupedImages;
};

const getInitialState = (images: ImagesByName) => {
  let initialState: ReleasesWithArches = {};

  Object.keys(images).forEach((distro) => {
    images[distro].forEach((image) => {
      if (!initialState[getValueKey(distro, image.release)]) {
        initialState[getValueKey(distro, image.release)] = [];
      }
    });
  });

  return initialState;
};

const getValueKey = (distro: string, release: string) => `${distro}-${release}`.replace(".", "-");

const DownloadImages = () => {
  // TODO: replace with useInfiniteQuery https://warthogs.atlassian.net/browse/MAASENG-2601
  const { data, isPending, isError, error } = useUpstreamImagesQuery({ page: 1, size: 10 });

  const {
    data: upstreamSourceData,
    isPending: isUpstreamSourcePending,
    isError: isUpstreamImageSourceError,
    error: upstreamImageSourceError,
  } = useUpstreamImageSourceQuery();

  const [images, setImages] = useState<ImagesByName>({});
  const [groupedImages, setGroupedImages] = useState<GroupedImages>({});
  const [initialValues, setInitialValues] = useState<ReleasesWithArches>({});

  const headingId = useId();

  useEffect(() => {
    if (data) {
      const imagesByName = groupImagesByName(data.items);
      setImages(imagesByName);
      setGroupedImages(groupArchesByRelease(imagesByName));
      setInitialValues(getInitialState(imagesByName));
    }
  }, [data]);

  const { setSidebar } = useAppLayoutContext();

  const resetForm = () => {
    setSidebar(null);
    setInitialValues(images ? getInitialState(images) : {});
  };

  const selectUpstreamImages = useSelectUpstreamImagesMutation({
    onSuccess() {
      resetForm();
    },
  });

  const handleSubmit = (
    values: ReleasesWithArches,
    images: UpstreamImage[],
    helpers: FormikHelpers<ReleasesWithArches>,
  ) => {
    const submitData = images.map((image) => ({
      id: image.id,
      download: values[getValueKey(image.codename, image.release)].some((item) => item.value === image.id),
    }));

    selectUpstreamImages.mutate(submitData);
    helpers.setSubmitting(false);
  };

  return (
    <ContentSection>
      {isUpstreamSourcePending ? (
        <Spinner text="Loading..." />
      ) : isError ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage error={error} />
        </Notification>
      ) : isUpstreamImageSourceError ? (
        <Notification severity="negative" title="Error">
          <ErrorMessage error={upstreamImageSourceError} />
        </Notification>
      ) : upstreamSourceData ? (
        <>
          <ContentSection.Header>
            <ContentSection.Title id={headingId}>
              Download images from {upstreamSourceData.upstreamSource}
            </ContentSection.Title>
            <p>
              Below you can select which images should be downloaded
              {upstreamSourceData.keepUpdated ? " and synced daily" : null} from{" "}
              <ExternalLink to={upstreamSourceData.upstreamSource}>{upstreamSourceData.upstreamSource}</ExternalLink> to
              the Site Manager image server. Images will be made available to connected MAAS sites.
            </p>
          </ContentSection.Header>
          <ContentSection.Content>
            {isPending ? (
              <Spinner text="Loading..." />
            ) : groupedImages && data ? (
              <Formik
                enableReinitialize={true}
                initialValues={initialValues}
                onSubmit={(values, helpers) => handleSubmit(values, data.items, helpers)}
              >
                {({ isSubmitting, dirty, values, setFieldValue }) => (
                  <Form aria-labelledby={headingId}>
                    {selectUpstreamImages.isError && (
                      <Notification severity="negative" title="Error while selecting images">
                        <ErrorMessage error={selectUpstreamImages.error} />
                      </Notification>
                    )}
                    {Object.keys(groupedImages).map((distro) => (
                      <span key={distro}>
                        <h2 className="p-heading--4">{distro} images</h2>
                        <table className="download-images-table">
                          <thead>
                            <tr>
                              <th>Release</th>
                              <th>Architecture</th>
                            </tr>
                          </thead>
                          <tbody>
                            {Object.keys(groupedImages[distro]).map((release) => (
                              <tr aria-label={release} key={release}>
                                <td>{release}</td>
                                <td>
                                  <Field
                                    as={MultiSelect}
                                    items={groupedImages[distro][release]}
                                    name={`${distro}-${release}`}
                                    onItemsUpdate={(items: MultiSelectItem) =>
                                      setFieldValue(getValueKey(distro, release), items)
                                    }
                                    placeholder="Select architectures"
                                    selectedItems={values[getValueKey(distro, release)]}
                                    variant="condensed"
                                  />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </span>
                    ))}
                    <ContentSection.Footer>
                      <Button appearance="base" onClick={resetForm} type="button">
                        Cancel
                      </Button>
                      <ActionButton
                        appearance="positive"
                        disabled={!dirty || isSubmitting || selectUpstreamImages.isPending}
                        loading={isSubmitting || selectUpstreamImages.isPending}
                        type="submit"
                      >
                        Save
                      </ActionButton>
                    </ContentSection.Footer>
                  </Form>
                )}
              </Formik>
            ) : null}
          </ContentSection.Content>
        </>
      ) : null}
    </ContentSection>
  );
};

export default DownloadImages;
