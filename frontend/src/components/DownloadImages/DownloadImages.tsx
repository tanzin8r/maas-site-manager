import type { MultiSelectItem } from "@canonical/maas-react-components";
import { ContentSection, ExternalLink, MultiSelect } from "@canonical/maas-react-components";
import { ActionButton, Button, Spinner } from "@canonical/react-components";
import { Field, Form, Formik } from "formik";

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
    if (!!imagesByName[image.name]) {
      imagesByName[image.name].push(image);
    } else {
      imagesByName[image.name] = [image];
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
        groupedImages[distro][image.release] = [{ label: image.architecture, value: image.id }];
      } else {
        groupedImages[distro][image.release].push({ label: image.architecture, value: image.id });
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
  const { data, isPending } = useUpstreamImagesQuery({ page: 1, size: 10 });

  const { data: upstreamSourceData, isPending: isUpstreamSourcePending } = useUpstreamImageSourceQuery();

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

  const handleSubmit = (values: ReleasesWithArches, images: UpstreamImage[]) => {
    const submitData = images.map((image) => ({
      id: image.id,
      download: values[getValueKey(image.name, image.release)].some((item) => item.value === image.id),
    }));

    selectUpstreamImages.mutate(submitData);
  };

  return (
    <ContentSection>
      {isUpstreamSourcePending ? (
        <Spinner text="Loading..." />
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
                onSubmit={(values) => handleSubmit(values, data.items)}
              >
                {({ isSubmitting, dirty, values, setFieldValue }) => (
                  <Form aria-labelledby={headingId}>
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
