import type { RenderResult } from "@testing-library/react";
import { rest } from "msw";

import EditRegion from "./EditRegion";

import urls from "@/api/urls";
import { RegionDetailsContext } from "@/context/RegionDetailsContext";
import { siteFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { render, waitFor, screen, userEvent, setupServer } from "@/utils/test-utils";

const region = siteFactory.build();
const mockServer = setupServer(rest.get(`${urls.sites}/:id`, createMockSiteResolver([region])));

const renderForm = async (): Promise<RenderResult> => {
  const { ...rendered } = render(
    <RegionDetailsContext.Provider value={{ regionId: region.id, setRegionId: vi.fn() }}>
      <EditRegion />
    </RegionDetailsContext.Provider>,
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

  expect(screen.getByRole("heading", { name: `Edit ${region.name}` })).toBeInTheDocument();

  expect(screen.getByRole("textbox", { name: "Street" })).toHaveValue(region.street);
  expect(screen.getByRole("textbox", { name: "City" })).toHaveValue(region.city);
  expect(screen.getByRole("textbox", { name: "Zip" })).toHaveValue(region.zip);
  expect(screen.getByRole("textbox", { name: "Latitude and Longitude" })).toHaveValue(
    `${region.latitude}, ${region.longitude}`,
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
