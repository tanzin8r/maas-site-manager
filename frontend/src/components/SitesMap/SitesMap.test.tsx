import SitesMap from "@/components/SitesMap";
import { siteFactory } from "@/mocks/factories";
import { sitesResolvers } from "@/testing/resolvers/sites";
import { usersResolvers } from "@/testing/resolvers/users";
import { renderWithMemoryRouter, screen, setupServer } from "@/utils/test-utils";

const sites = siteFactory.buildList(2);
const mockServer = setupServer(sitesResolvers.sitesCoordinates.handler(sites), usersResolvers.getCurrentUser.handler());

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
