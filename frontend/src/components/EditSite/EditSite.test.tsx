import { rest } from "msw";

import EditSite from "./EditSite";

import { SiteDetailsContext } from "@/context/SiteDetailsContext";
import { siteFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, userEvent, setupServer, waitForLoadingToFinish } from "@/utils/test-utils";

const site = siteFactory.build();
const mockServer = setupServer(rest.get(`${apiUrls.sites}/:id`, createMockSiteResolver([site])));

const renderForm = async () => {
  const view = render(
    <SiteDetailsContext.Provider value={{ selected: site.id, setSelected: vi.fn() }}>
      <EditSite />
    </SiteDetailsContext.Provider>,
  );
  await waitForLoadingToFinish();

  return view;
};

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("prefills form data", async () => {
  await renderForm();

  expect(screen.getByRole("heading", { name: `Edit ${site.name}` })).toBeInTheDocument();

  expect(screen.getByRole("combobox", { name: "Country/Region" })).toHaveValue(site.country);
  expect(screen.getByRole("textbox", { name: "Administrative region" })).toHaveValue(site.state);
  expect(screen.getByRole("textbox", { name: "City" })).toHaveValue(site.city);
  expect(screen.getByRole("textbox", { name: "Address" })).toHaveValue(site.address);
  expect(screen.getByRole("textbox", { name: "Postal code" })).toHaveValue(site.postal_code);
  expect(screen.getByRole("textbox", { name: "Latitude and Longitude" })).toHaveValue(
    `${site.coordinates![0]}, ${site.coordinates![1]}`,
  );
});

it("enables the submit button only when values have been changed while editing", async () => {
  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "City" }));

  expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
});

it("displays an error if non-coordinate text is entered into the coordinates field", async () => {
  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "Latitude and Longitude" }));

  await userEvent.type(screen.getByRole("textbox", { name: "Latitude and Longitude" }), "this is not co-ordinates");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Latitude and Longitude input can only contain numerical characters \(0-9\), a decimal point \(.\), a comma \(,\), or a minus \(-\)./i,
    ),
  ).toBeInTheDocument();
});

it("displays an error if invalid coordinates are entered", async () => {
  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "Latitude and Longitude" }));

  // Maximum longitude is 180
  await userEvent.type(screen.getByRole("textbox", { name: "Latitude and Longitude" }), "69.4200, 420.69");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma \(,\)./i,
    ),
  ).toBeInTheDocument();
});

it("displays the 'Invalid' message for coordinates with a decimal point but no decimals", async () => {
  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "Latitude and Longitude" }));

  await userEvent.type(screen.getByRole("textbox", { name: "Latitude and Longitude" }), "69., -69.");

  await userEvent.tab();

  expect(
    screen.getByText(
      /Invalid latitude and longitude. Please make sure the coordinates provided are valid and separated by a comma \(,\)./i,
    ),
  ).toBeInTheDocument();
});
