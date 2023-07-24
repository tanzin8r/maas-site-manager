/* eslint-disable testing-library/no-node-access */
import { allResolvers } from "@/mocks/resolvers";
import { act, waitFor, setupServer } from "@/utils/test-utils";

const mockServer = setupServer(...allResolvers);

beforeAll(() => {
  mockServer.listen();

  const rootElement = document.createElement("div");
  rootElement.setAttribute("id", "root");
  document.body.appendChild(rootElement);
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("renders the app in the root element", async () => {
  await act(() => import("./main"));
  const container = document.getElementById("root") as HTMLElement;
  await waitFor(() => expect(container.querySelector(".l-application")).toBeInTheDocument());
});
