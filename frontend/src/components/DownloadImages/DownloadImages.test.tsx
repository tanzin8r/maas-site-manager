import { rest } from "msw";

import DownloadImages from "./DownloadImages";

import type { UpstreamImage } from "@/api";
import { upstreamImageFactory, upstreamImageSourceFactory } from "@/mocks/factories";
import {
  createMockSelectUpstreamImagesResolver,
  createMockUpstreamImageSourceResolver,
  createMockUpstreamImagesResolver,
} from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const ubuntuImages = upstreamImageFactory.buildList(5, { codename: "Ubuntu" });
const centOsImages = upstreamImageFactory.buildList(5, { codename: "CentOS" });
const upstreamImages = [...ubuntuImages, ...centOsImages];
const upstreamImageSource = upstreamImageSourceFactory.build({
  upstreamSource: "https://images.example.com",
  keepUpdated: true,
});

const upstreamImagesHandler = rest.get(apiUrls.upstreamImages, createMockUpstreamImagesResolver(upstreamImages));
const upstreamImageSourceHandler = rest.get(
  apiUrls.upstreamImageSource,
  createMockUpstreamImageSourceResolver(upstreamImageSource),
);
const selectUpstreamImagesHandler = rest.post(apiUrls.upstreamImages, createMockSelectUpstreamImagesResolver());

const handlers = [upstreamImagesHandler, upstreamImageSourceHandler, selectUpstreamImagesHandler];

const mockServer = setupServer(...handlers);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
  localStorage.clear();
});

afterAll(() => {
  mockServer.close();
});

it("displays the image source in the header", async () => {
  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(
      screen.getByRole("heading", { name: "Download images from https://images.example.com" }),
    ).toBeInTheDocument();
  });
});

it("displays '...and synced daily' if daily sync is enabled", async () => {
  const { unmount } = renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByText(/and synced daily/i)).toBeInTheDocument();
  });

  unmount();

  const notSyncedUpstreamSource = upstreamImageSourceFactory.build({ keepUpdated: false });

  mockServer.resetHandlers(
    upstreamImagesHandler,
    rest.get(apiUrls.upstreamImageSource, createMockUpstreamImageSourceResolver(notSyncedUpstreamSource)),
    selectUpstreamImagesHandler,
  );

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.queryByText(/and synced daily/i)).not.toBeInTheDocument();
  });
});

it("separates images by distro", async () => {
  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByRole("heading", { name: /Ubuntu images/i })).toBeInTheDocument();
  });

  expect(screen.getByRole("heading", { name: /CentOS images/i })).toBeInTheDocument();
});

it("enables the submit button once the form has been edited", async () => {
  let images: UpstreamImage[] = [];
  const arches = ["amd64", "arm64", "i386"];

  arches.forEach((architecture) => {
    images.push(upstreamImageFactory.build({ codename: "Ubuntu", release: "22.04 LTS", arch: architecture }));
  });

  const localHandlers = [
    rest.get(apiUrls.upstreamImages, createMockUpstreamImagesResolver(images)),
    upstreamImageSourceHandler,
    selectUpstreamImagesHandler,
  ];

  mockServer.resetHandlers(...localHandlers);

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByRole("form", { name: /Download images/i })).toBeInTheDocument();
  });

  expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();

  await waitFor(() => expect(screen.getByRole("combobox", { name: "Select architectures" })).toBeInTheDocument());

  await userEvent.click(screen.getByRole("combobox", { name: "Select architectures" }));

  arches.forEach(async (arch) => {
    await userEvent.click(screen.getByRole("checkbox", { name: arch }));
  });

  await waitFor(() => {
    expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
  });
});

it("displays errors that ocurred while fetching images", async () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.upstreamImages, (req, res, ctx) => {
      return res(ctx.status(400, "error"));
    }),
    upstreamImageSourceHandler,
  );

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByText("Error")).toBeInTheDocument();
  });
});

it("displays errors that ocurred while fetching the upstream image source", async () => {
  mockServer.resetHandlers(
    rest.get(apiUrls.upstreamImageSource, (req, res, ctx) => {
      return res(ctx.status(400, "error"));
    }),
    upstreamImagesHandler,
  );

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByText("Error")).toBeInTheDocument();
  });
});

// this will be fixed in https://warthogs.atlassian.net/browse/MAASENG-4706
it.skip("displays errors that ocurred after submitting image selection", async () => {
  let images: UpstreamImage[] = [];
  const arches = ["amd64", "arm64", "i386"];

  arches.forEach((architecture) => {
    images.push(upstreamImageFactory.build({ codename: "Ubuntu", release: "22.04 LTS", arch: architecture }));
  });

  const localHandlers = [
    rest.get(apiUrls.upstreamImages, createMockUpstreamImagesResolver(images)),
    upstreamImageSourceHandler,
    rest.post(apiUrls.upstreamImages, (req, res, ctx) => {
      throw res(ctx.status(400, "error"));
    }),
  ];

  mockServer.resetHandlers(...localHandlers);

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByRole("form", { name: /Download images/i })).toBeInTheDocument();
  });
  expect(screen.getByRole("button", { name: "Save" })).toBeDisabled();

  await waitFor(() => expect(screen.getByRole("combobox", { name: "Select architectures" })).toBeInTheDocument());

  await userEvent.click(screen.getByRole("combobox", { name: "Select architectures" }));

  await userEvent.click(screen.getByRole("checkbox", { name: "amd64" }));

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText(/Error/i)).toBeInTheDocument();
  });
});
