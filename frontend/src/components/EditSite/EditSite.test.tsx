import { rest } from "msw";

import EditSite from "./EditSite";

import type { MutationErrorResponse } from "@/api";
import { ExceptionCode } from "@/api";
import { SiteDetailsContext } from "@/context/SiteDetailsContext";
import { siteFactory } from "@/mocks/factories";
import { createMockSiteResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { render, screen, userEvent, setupServer, waitForLoadingToFinish, waitFor } from "@/utils/test-utils";

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
    `${site.coordinates?.latitude}, ${site.coordinates?.longitude}`,
  );
});

it("shows errors when fetching the site", async () => {
  mockServer.use(rest.get(`${apiUrls.sites}/:id`, (req, res, ctx) => res(ctx.status(500))));

  await renderForm();

  expect(screen.getByText(/Error while fetching site/i)).toBeInTheDocument();
});

it("enables the submit button only when values have been changed while editing", async () => {
  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "City" }));

  expect(screen.getByRole("button", { name: "Save" })).toBeEnabled();
});

it("shows errors after submission", async () => {
  mockServer.use(
    rest.patch(`${apiUrls.sites}/:id`, (req, res, ctx) => {
      return res(ctx.status(400), ctx.json({ error: { message: "Uh oh!" } }));
    }),
  );

  await renderForm();

  await userEvent.type(screen.getByRole("textbox", { name: "City" }), "Dundee");

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText(/Error while updating site/i)).toBeInTheDocument();
  });
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

it("displays error messages from the backend on the coordinates field", async () => {
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
    rest.patch(`${apiUrls.sites}/:id`, (req, res, ctx) => {
      return res(ctx.status(400), ctx.json(errorResponse.body));
    }),
  );

  await renderForm();

  await userEvent.clear(screen.getByRole("textbox", { name: "Latitude and Longitude" }));

  await userEvent.type(screen.getByRole("textbox", { name: "Latitude and Longitude" }), "50, 50");

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText("Invalid coordinates")).toBeInTheDocument();
  });
});
