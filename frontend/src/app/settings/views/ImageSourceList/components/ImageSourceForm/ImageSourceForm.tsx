import { useEffect, useId, useState } from "react";

import { ContentSection } from "@canonical/maas-react-components";
import { ActionButton, Button, Input, Label, Notification, Spinner, Textarea } from "@canonical/react-components";
import { Field, Formik } from "formik";
import * as Yup from "yup";

import type { MutationErrorResponse } from "@/app/api";
import { useCreateImageSource, useImageSource, useUpdateImageSource } from "@/app/api/query/imageSources";
import type {
  PatchBootSourceV1BootassetSourcesIdPatchData,
  PostBootSourcesV1BootassetSourcesPostData,
} from "@/app/apiclient";
import ErrorMessage from "@/app/base/components/ErrorMessage";
import FormikFormContent from "@/app/base/components/FormikFormContent";
import { useAppLayoutContext } from "@/app/context";
import { useBootSourceContext } from "@/app/context/BootSourceContext";

const baseInitialValues = {
  name: "",
  url: "",
  keyring: "",
  priority: 1,
  autosync: true,
};

type ImageSourceFormValues = typeof baseInitialValues;

const ImageSourceSchema = Yup.object().shape({
  name: Yup.string(),
  url: Yup.string().url("Not a valid URL").required("URL is required"),
  keyring: Yup.string(),
  priority: Yup.number().integer("Priority must be a whole number").required("Priority is required"),
  autosync: Yup.boolean(),
});

const ImageSourceForm = ({ type }: { type: "add" | "edit" }) => {
  const { selected: selectedBootSourceId, setSelected } = useBootSourceContext();
  const { setSidebar } = useAppLayoutContext();
  const [initialValues, setInitialValues] = useState<ImageSourceFormValues>(baseInitialValues);

  const createImageSource = useCreateImageSource();
  const updateImageSource = useUpdateImageSource();
  const {
    data: imageSource,
    error,
    isPending,
  } = useImageSource({ path: { id: selectedBootSourceId! } }, type === "edit");

  const headingId = useId();
  const nameFieldId = useId();
  const urlFieldId = useId();
  const keyringFieldId = useId();
  const priorityFieldId = useId();
  const autosyncFieldId = useId();

  const isMutationPending = createImageSource.isPending || updateImageSource.isPending;

  // Make sure initialValues are only set once data is fully loaded
  useEffect(() => {
    if (type === "edit" && imageSource) {
      setInitialValues({
        name: imageSource.name || "",
        url: imageSource.url || "",
        keyring: imageSource.keyring || "",
        priority: imageSource.priority || 1,
        autosync: imageSource.sync_interval !== undefined ? imageSource.sync_interval > 0 : true,
      });
    } else if (type === "add") {
      setInitialValues(baseInitialValues);
    }
  }, [type, imageSource]);

  const resetForm = () => {
    setSelected(null);
    setSidebar(null);
    setInitialValues(baseInitialValues);
  };

  const handleSubmit = (values: ImageSourceFormValues) => {
    const body:
      | PatchBootSourceV1BootassetSourcesIdPatchData["body"]
      | PostBootSourcesV1BootassetSourcesPostData["body"] = {
      name: values.name,
      url: values.url,
      keyring: values.keyring,
      priority: values.priority,
      sync_interval: values.autosync ? 60 : 0,
    };
    if (type === "add") {
      createImageSource.mutate({ body } as PostBootSourcesV1BootassetSourcesPostData, { onSuccess: resetForm });
    } else {
      updateImageSource.mutate(
        {
          path: { id: selectedBootSourceId! },
          body,
        } as PatchBootSourceV1BootassetSourcesIdPatchData,
        { onSuccess: resetForm },
      );
    }
  };

  return (
    <ContentSection>
      <ContentSection.Title id={headingId}>
        {type === "add" ? "Add image source" : `Edit ${imageSource ? imageSource.url : "image source"}`}
      </ContentSection.Title>
      <ContentSection.Content>
        {error ? (
          <Notification severity="negative" title="Error while fetching image source">
            <ErrorMessage error={error} />
          </Notification>
        ) : null}
        {updateImageSource.isError && (
          <Notification severity="negative" title="Error while editing image source">
            <ErrorMessage error={updateImageSource.error} />
          </Notification>
        )}
        {createImageSource.isError && (
          <Notification severity="negative" title="Error while adding image source">
            <ErrorMessage error={createImageSource.error} />
          </Notification>
        )}
        {type === "edit" && (isPending || !imageSource) ? (
          <Spinner text="Loading..." />
        ) : (
          <Formik
            enableReinitialize={true}
            initialValues={initialValues}
            onSubmit={handleSubmit}
            validationSchema={ImageSourceSchema}
          >
            {({ errors, isSubmitting, touched, dirty, isValid }) => (
              <FormikFormContent
                aria-labelledby={headingId}
                errors={
                  [
                    { body: createImageSource.error?.response?.data },
                    { body: updateImageSource.error?.response?.data },
                  ] as MutationErrorResponse[]
                }
              >
                <Label htmlFor={nameFieldId}>Name</Label>
                <Field as={Input} error={touched.name && errors.name} id={nameFieldId} name="name" type="text" />
                <Label className="is-required" htmlFor={urlFieldId}>
                  URL
                </Label>
                <Field
                  as={Input}
                  caution={
                    type === "edit"
                      ? "Changing to an image server with different images might remove some images from MAAS Site Manager and MAAS."
                      : null
                  }
                  error={touched.url && errors.url}
                  id={urlFieldId}
                  name="url"
                  required
                  type="text"
                />
                <Label htmlFor={keyringFieldId}>GPG key</Label>
                <Field
                  as={Textarea}
                  className="u-textarea-no-resize--horizontal"
                  help="An optional GPG public key to verify the authenticity of the image source."
                  id={keyringFieldId}
                  name="keyring"
                />
                <Label className="is-required" htmlFor={priorityFieldId}>
                  Priority
                </Label>
                <Field
                  as={Input}
                  error={touched.priority && errors.priority}
                  help="If the same image is available from several sources, the image from the source with the higher priority takes precedence. 1 is the highest priority."
                  id={priorityFieldId}
                  name="priority"
                  required
                  type="text"
                />
                <Label className="u-no-margin" htmlFor={autosyncFieldId}>
                  Syncing
                </Label>
                <p className="u-text--muted u-no-margin">
                  Site Manager will check if selected images have been updated at the image source and sync them, if
                  available.
                </p>
                <Field as={Input} label="Automatically sync images" name="autosync" type="checkbox" />

                <hr />
                <div className="u-flex u-flex--justify-end u-padding-top--medium">
                  <Button appearance="base" onClick={resetForm} type="button">
                    Cancel
                  </Button>
                  <ActionButton
                    appearance="positive"
                    disabled={!dirty || !isValid || isSubmitting || isMutationPending}
                    loading={isSubmitting || isMutationPending}
                    type="submit"
                  >
                    {type === "add" ? "Add image source" : "Save"}
                  </ActionButton>
                </div>
              </FormikFormContent>
            )}
          </Formik>
        )}
      </ContentSection.Content>
    </ContentSection>
  );
};

export default ImageSourceForm;
