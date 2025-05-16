import { setupServer } from "msw/node";

import {
  useCreateImageSource,
  useDeleteImageSource,
  useImageSource,
  useImageSources,
  useUpdateImageSource,
} from "@/api/query/imageSources";
import type { BootSourcesPatchRequest, BootSourcesPostRequest } from "@/apiclient";
import { imageSourceFactory } from "@/mocks/factories";
import { imageSourceResolvers } from "@/testing/resolvers/imageSources";
import { Providers, renderHook, waitFor } from "@/utils/test-utils";

const imageSources = imageSourceFactory.buildList(15);
const mockServer = setupServer(
  imageSourceResolvers.listImageSources.handler(imageSources),
  imageSourceResolvers.getImageSource.handler(imageSources),
  imageSourceResolvers.createImageSource.handler(),
  imageSourceResolvers.updateImageSource.handler(),
  imageSourceResolvers.deleteImageSource.handler(),
);

beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

describe("useImageSources", () => {
  it("should return boot sources data", async () => {
    const { result } = renderHook(
      () =>
        useImageSources({
          query: {
            page: 1,
            size: 10,
          },
        }),
      { wrapper: Providers },
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data.items).toHaveLength(imageSources.length);
    expect(result.current.data.items).toEqual(imageSources);
  });

  it("should fetch all pages automatically", async () => {
    const { result } = renderHook(() => useImageSources(), { wrapper: Providers });

    await waitFor(
      () => {
        expect(result.current.data.items).toHaveLength(15);
      },
      { timeout: 5000 },
    );

    expect(result.current.data.items).toEqual(imageSources);
    expect(result.current.hasNextPage).toBe(false);
  });
});

describe("useImageSource", () => {
  it("should return a specific boot source", async () => {
    const expectedSource = imageSources[0];
    const { result } = renderHook(() => useImageSource({ path: { id: expectedSource.id } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(expectedSource);
  });

  it("should return error if boot source does not exist", async () => {
    const { result } = renderHook(() => useImageSource({ path: { id: 999 } }), {
      wrapper: Providers,
    });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });

  it("should not fetch when disabled", async () => {
    const { result } = renderHook(() => useImageSource({ path: { id: 1 } }, false), {
      wrapper: Providers,
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.isFetching).toBe(false);
  });
});

describe("useCreateImageSource", () => {
  it("should create a new boot source", async () => {
    const newSource: BootSourcesPostRequest = {
      url: "https://example.com/image.iso",
      priority: 1,
      keyring: "",
      sync_interval: 100,
    };

    const { result } = renderHook(() => useCreateImageSource(), { wrapper: Providers });
    result.current.mutate({ body: newSource });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.id).toBeDefined();
  });
});

describe("useUpdateImageSource", () => {
  it("should update an existing boot source", async () => {
    const sourceToUpdate = imageSources[0];
    const updateData: BootSourcesPatchRequest = {
      priority: 2,
    };

    const { result } = renderHook(() => useUpdateImageSource(), { wrapper: Providers });
    result.current.mutate({ body: updateData, path: { id: sourceToUpdate.id } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});

describe("useDeleteImageSource", () => {
  it("should delete a boot source", async () => {
    const sourceToDelete = imageSources[0];

    const { result } = renderHook(() => useDeleteImageSource(), { wrapper: Providers });
    result.current.mutate({ path: { id: sourceToDelete.id } });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
