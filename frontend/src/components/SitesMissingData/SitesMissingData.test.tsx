import { http, HttpResponse } from "msw";

import SitesMissingData from "./SitesMissingData";

import type { MutationErrorResponse } from "@/api";
import { ExceptionCode } from "@/api";
import { siteFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { apiUrls } from "@/utils/test-urls";
import {
  setupServer,
  waitForLoadingToFinish,
  screen,
  renderWithMemoryRouter,
  userEvent,
  waitFor,
} from "@/utils/test-utils";

const sites = siteFactory.buildList(5, { coordinates: null });
const mockServer = setupServer(sitesResolvers.listSites.handler(sites));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays a list of sites with missing coordinates", async () => {
  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  sites.forEach((site) => {
    expect(screen.getByText(site.name)).toBeInTheDocument();
    expect(screen.getByText(`${site.url}`)).toBeInTheDocument();
  });
});

it("enables the submit button once a site's coordinates have been changed", async () => {
  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  await userEvent.click(screen.getAllByRole("tab")[0]);

  const input = screen.getByRole("textbox");

  expect(screen.getByRole("button", { name: "Save" })).toBeAriaDisabled();

  await userEvent.type(input, "1, 1");

  expect(screen.getByRole("button", { name: "Save" })).not.toBeAriaDisabled();
});

it("displays an error if non-coordinate text is entered", async () => {
  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  await userEvent.click(screen.getAllByRole("tab")[0]);

  const input = screen.getByRole("textbox");

  await userEvent.type(input, "invalid coordinates");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Latitude and Longitude input can only contain numerical characters \(0-9\), a decimal point \(.\), a comma \(,\), or a minus \(-\)./i,
    ),
  ).toBeInTheDocument();
});

it("displays an error if invalid coordinates are entered", async () => {
  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  await userEvent.click(screen.getAllByRole("tab")[0]);

  const input = screen.getByRole("textbox");

  await userEvent.type(input, "69.420, 420.69");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma \(,\)./i,
    ),
  ).toBeInTheDocument();
});

it("displays the 'invalid' message for coordinates with a decimal point but no decimals", async () => {
  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  await userEvent.click(screen.getAllByRole("tab")[0]);

  const input = screen.getByRole("textbox");

  await userEvent.type(input, "69., -69.");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma \(,\)./i,
    ),
  ).toBeInTheDocument();
});

it("displays error messages if sites fail to fetch", async () => {
  mockServer.use(http.get(`${apiUrls.sites}`, () => new HttpResponse(null, { status: 500 })));

  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();

  expect(screen.getByText(/Error while fetching sites/i)).toBeInTheDocument();
});

it("displays error messages after failed submission", async () => {
  const errorResponse: MutationErrorResponse = {
    body: {
      error: {
        code: ExceptionCode.INVALID_PARAMETERS,
        message: "Validation error",
        details: [
          {
            messages: ["Invalid coordinates"],
            field: "coordinates.latitude",
            reason: "Validation error",
          },
        ],
      },
    },
  };

  mockServer.use(
    http.patch(`${apiUrls.sites}/:id`, () => {
      return new HttpResponse(JSON.stringify(errorResponse.body), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }),
    sitesResolvers.updateSites.handler(),
  );

  renderWithMemoryRouter(<SitesMissingData />);

  await waitForLoadingToFinish();
  await userEvent.click(screen.getAllByRole("tab")[0]);

  const input = screen.getByRole("textbox");

  await userEvent.type(input, "1, 1");
  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText(/Error while updating sites/i)).toBeInTheDocument();
  });

  await waitFor(() => {
    expect(screen.getByText(/Invalid coordinates/i)).toBeInTheDocument();
  });
});
