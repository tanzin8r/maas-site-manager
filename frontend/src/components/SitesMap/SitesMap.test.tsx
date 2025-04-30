import { rest } from "msw";

import SitesMap from "@/components/SitesMap";
import { siteFactory } from "@/mocks/factories";
import { createMockCurrentUserResolver, createMockSitesCoordinatesResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen, setupServer } from "@/utils/test-utils";

const sites = siteFactory.buildList(2);
const mockServer = setupServer(
  rest.get(apiUrls.sitesCoordinates, createMockSitesCoordinatesResolver(sites)),
  rest.get(apiUrls.currentUser, createMockCurrentUserResolver()),
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

it("renders map with controls", () => {
  renderWithMemoryRouter(<SitesMap />);

  expect(screen.getByRole("region", { name: /sites map/i })).toBeInTheDocument();
});
