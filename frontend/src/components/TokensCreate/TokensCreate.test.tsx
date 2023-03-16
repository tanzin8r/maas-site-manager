import TokensCreate from "./TokensCreate";

import { render, screen } from "@/test-utils";

describe("TokensCreate", () => {
  it("renders the form", async () => {
    render(<TokensCreate />);
    expect(screen.getByRole("form", { name: /Generate new enrollment tokens/i })).toBeInTheDocument();
  });
});
