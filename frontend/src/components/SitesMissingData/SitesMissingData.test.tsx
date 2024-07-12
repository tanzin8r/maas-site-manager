import { rest } from "msw";

import SitesMissingData from "./SitesMissingData";

import { siteFactory } from "@/mocks/factories";
import { createMockSitesResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { setupServer, waitForLoadingToFinish, screen, renderWithMemoryRouter, userEvent } from "@/utils/test-utils";

const sites = siteFactory.buildList(5, { coordinates: null });
const mockServer = setupServer(rest.get(`${apiUrls.sites}`, createMockSitesResolver(sites)));

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
