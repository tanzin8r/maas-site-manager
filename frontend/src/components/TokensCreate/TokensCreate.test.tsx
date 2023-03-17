import { rest } from "msw";
import { setupServer } from "msw/node";
import { vi } from "vitest";

import TokensCreate from "./TokensCreate";

import urls from "@/api/urls";
import { renderWithMemoryRouter, screen, userEvent } from "@/test-utils";

const postTokensEndpointMock = vi.fn();
const mockServer = setupServer(
  rest.post(urls.tokens, async (req) => {
    postTokensEndpointMock(await req.json());
  }),
);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

describe("TokensCreate", () => {
  it("renders the form", async () => {
    renderWithMemoryRouter(<TokensCreate />);
    expect(screen.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeInTheDocument();
  });

  it("if not all required fields have been entered the submit button is disabled", async () => {
    renderWithMemoryRouter(<TokensCreate />);
    const amount = screen.getByLabelText(/Amount of tokens to generate/i);
    const expires = screen.getByLabelText(/Expiration time/i);
    expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeDisabled();
    await userEvent.type(amount, "1");
    await userEvent.type(expires, "1 month");
    expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeEnabled();
  });

  it("displays an error for invalid expiration value", async () => {
    renderWithMemoryRouter(<TokensCreate />);
    const expires = screen.getByLabelText(/Expiration time/i);
    await userEvent.type(expires, "2");
    await userEvent.tab();
    expect(expires).toHaveErrorMessage(
      /Time unit must be a `string` type with a value of weeks, days, hours, and\/or minutes./i,
    );
  });

  it("can generate enrolment tokens", async () => {
    renderWithMemoryRouter(<TokensCreate />);
    const amount = screen.getByLabelText(/Amount of tokens to generate/i);
    const expires = screen.getByLabelText(/Expiration time/i);
    expect(screen.getByRole("button", { name: /Generate tokens/i })).toBeDisabled();
    // can specify the number of tokens to generate
    await userEvent.type(amount, "1");
    // can specify the token expiration time (e.g. 1 week)
    await userEvent.type(expires, "1 week");
    await userEvent.click(screen.getByRole("button", { name: /Generate tokens/i }));
    expect(postTokensEndpointMock).toHaveBeenCalledTimes(1);
    expect(postTokensEndpointMock).toHaveBeenCalledWith({
      amount: 1,
      expires: "P0Y0M7DT0H0M0S",
    });
  });
});
