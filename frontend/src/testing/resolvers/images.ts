import { http, HttpResponse } from "msw";

import type { ImageSource, SelectableImage, SelectedImage, UnauthorizedErrorBodyResponse } from "@/app/apiclient";
import { alternativeImageFactory, selectableImageFactory, selectedImageFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockSelectedImages = selectedImageFactory.buildList(30);
const mockSelectableImages = selectableImageFactory.buildList(30);
const mockAlternativeImages = alternativeImageFactory.buildList(5);

const mockUnauthorizedError: UnauthorizedErrorBodyResponse = {
  message: "You do not have permission to view this content.",
};

const imageResolvers = {
  selectedImages: {
    resolved: false,
    handler: (data: SelectedImage[] = mockSelectedImages) => {
      return http.get(apiUrls.selectedImages, async () => {
        const response = {
          items: data,
          total: data.length,
        };
        imageResolvers.selectedImages.resolved = true;
        return HttpResponse.json(response);
      });
    },
    error: (error = mockUnauthorizedError) => {
      return http.get(apiUrls.selectedImages, () => {
        imageResolvers.selectedImages.resolved = true;
        return HttpResponse.json(error, { status: 401 });
      });
    },
  },
  selectableImages: {
    resolved: false,
    handler: (data: SelectableImage[] = mockSelectableImages) => {
      return http.get(apiUrls.selectableImages, async () => {
        const response = {
          items: data,
          total: data.length,
        };
        imageResolvers.selectedImages.resolved = true;
        return HttpResponse.json(response);
      });
    },
    error: (error = mockUnauthorizedError) => {
      return http.get(apiUrls.selectableImages, () => {
        imageResolvers.selectedImages.resolved = true;
        return HttpResponse.json(error, { status: 401 });
      });
    },
  },
  getAlternativesForImage: {
    resolved: false,
    handler: (data: ImageSource[] = mockAlternativeImages) => {
      return http.get(apiUrls.alternativeImages, ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const os = searchParams.get("os");
        const release = searchParams.get("release");
        const arch = searchParams.get("arch");
        if (!(os && release && arch)) {
          return HttpResponse.json({ status: 422 });
        }
        const response = {
          items: data,
          total: data.length,
        };
        imageResolvers.getAlternativesForImage.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  addImageToSelection: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.addImageToSelection, async () => {
        imageResolvers.addImageToSelection.resolved = true;
        return new HttpResponse(null, { status: 201 });
      });
    },
  },
  removeImageFromSelection: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.removeImageFromSelection, async () => {
        imageResolvers.removeImageFromSelection.resolved = true;
        return new HttpResponse(null, { status: 204 });
      });
    },
  },
  uploadCustomImage: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.images, async () => {
        imageResolvers.uploadCustomImage.resolved = true;
        return new HttpResponse(null, { status: 201 });
      });
    },
    error: (error = mockUnauthorizedError) => {
      return http.post(apiUrls.images, () => {
        imageResolvers.uploadCustomImage.resolved = true;
        return HttpResponse.json(error, { status: 401 });
      });
    },
  },
  deleteCustomImage: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.removeImages, async () => {
        imageResolvers.deleteCustomImage.resolved = true;
        return new HttpResponse(null, { status: 204 });
      });
    },
    error: (error = mockUnauthorizedError) => {
      return http.post(apiUrls.removeImages, () => {
        imageResolvers.deleteCustomImage.resolved = true;
        return HttpResponse.json(error, { status: 401 });
      });
    },
  },
};

export { imageResolvers, mockSelectedImages, mockSelectableImages, mockAlternativeImages };
