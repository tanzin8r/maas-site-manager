import SitesMap from "@/components/SitesMap";
import { siteFactory } from "@/mocks/factories";
import { createMockSitesCoordinatesResolver } from "@/mocks/resolvers";
import { createMockGetServer } from "@/mocks/server";
import { apiUrls } from "@/utils/test-urls";
import { renderWithMemoryRouter, screen } from "@/utils/test-utils";

const sites = siteFactory.buildList(2);
const mockServer = createMockGetServer(apiUrls.sitesCoordinates, createMockSitesCoordinatesResolver(sites));

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
  expect(screen.getByRole("searchbox")).toBeInTheDocument();
});
