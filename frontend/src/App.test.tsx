/* eslint-disable testing-library/no-container */
import App from "./App";

import { allResolvers } from "@/mocks/resolvers";
import { waitFor, render, setupServer } from "@/test-utils";

const mockServer = setupServer(...allResolvers);
beforeAll(() => {
  mockServer.listen();
});
afterEach(() => {
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("renders vanilla layout components correctly", async () => {
  const { container } = render(<App />);
  await waitFor(() => expect(container.querySelector(".l-application")).toBeInTheDocument());
  const application = container.querySelector(".l-application") as HTMLElement;
  expect(application.querySelector(".l-navigation-bar")).toBeInTheDocument();
  expect(application.querySelector(".l-main")).toBeInTheDocument();
  expect(application.querySelector(".l-navigation-bar")).toBeInTheDocument();
});
