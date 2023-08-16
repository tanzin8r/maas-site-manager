import type { RenderResult } from "@testing-library/react";
import { rest } from "msw";

import EditSite from "./EditSite";

import { SiteDetailsContext } from "@/context/SiteDetailsContext";
import { siteFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { render, waitFor, screen, userEvent, setupServer } from "@/utils/test-utils";

const site = siteFactory.build();
const mockServer = setupServer(rest.get(`${apiUrls.sites}/:id`, createMockSiteResolver([site])));

const renderForm = async (): Promise<RenderResult> => {
  const { ...rendered } = render(
    <SiteDetailsContext.Provider value={{ selected: site.id, setSelected: vi.fn() }}>
      <EditSite />
    </SiteDetailsContext.Provider>,
  );
  // Wait for form to load
  await waitFor(async () => {
    expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument();
  });

  return rendered;
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

  expect(screen.getByRole("combobox", { name: "Country" })).toHaveValue(site.country);
  expect(screen.getByRole("textbox", { name: "Street" })).toHaveValue(site.street);
  expect(screen.getByRole("textbox", { name: "City" })).toHaveValue(site.city);
  expect(screen.getByRole("textbox", { name: "Latitude and Longitude" })).toHaveValue(
    `${site.latitude}, ${site.longitude}`,
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
