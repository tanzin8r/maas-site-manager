import { http, HttpResponse } from "msw";

import DownloadImages from "./DownloadImages";

import type { UpstreamImage } from "@/api";
import { upstreamImageFactory, upstreamImageSourceFactory } from "@/mocks/factories";
import { imagesResolvers } from "@/testing/resolvers/images";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

const ubuntuImages = upstreamImageFactory.buildList(5, { codename: "Ubuntu" });
const centOsImages = upstreamImageFactory.buildList(5, { codename: "CentOS" });
const upstreamImages = [...ubuntuImages, ...centOsImages];
const upstreamImageSource = upstreamImageSourceFactory.build({
  upstreamSource: "https://images.example.com",
  keepUpdated: true,
});

const mockServer = setupServer(
  imagesResolvers.listUpstreamImages.handler(upstreamImages),
  imagesResolvers.selectUpstreamImages.handler(),
  imagesResolvers.getImageSource.handler(upstreamImageSource),
);

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

  mockServer.use(
    imagesResolvers.listUpstreamImages.handler(upstreamImages),
    imagesResolvers.getImageSource.handler(notSyncedUpstreamSource),
    imagesResolvers.selectUpstreamImages.handler(),
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
    imagesResolvers.listUpstreamImages.handler(images),
    imagesResolvers.getImageSource.handler(upstreamImageSource),
    imagesResolvers.selectUpstreamImages.handler(),
  ];

  mockServer.use(...localHandlers);

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
  mockServer.use(
    http.get(apiUrls.upstreamImages, () => {
      return new HttpResponse(null, {
        status: 500,
        statusText: "error",
      });
    }),
    imagesResolvers.getImageSource.handler(upstreamImageSource),
  );

  renderWithMemoryRouter(<DownloadImages />);

  await waitFor(() => {
    expect(screen.getByText("Error")).toBeInTheDocument();
  });
});

it("displays errors that ocurred while fetching the upstream image source", async () => {
  mockServer.use(
    http.get(apiUrls.upstreamImageSource, () => {
      return HttpResponse.json(
        {},
        {
          status: 400,
        },
      );
    }),
    imagesResolvers.listUpstreamImages.handler(upstreamImages),
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

  mockServer.use(
    imagesResolvers.listUpstreamImages.handler(images),
    imagesResolvers.getImageSource.handler(upstreamImageSource),
    http.post(apiUrls.upstreamImages, () => {
      return HttpResponse.json(null, { status: 400, statusText: "error" });
    }),
  );

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
