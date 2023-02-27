import { render, screen } from "./test-utils";

import App from "./App";

describe("App", () => {
  it("renders headline", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: /MAAS Site Manager/i })
    ).toBeInTheDocument();
  });
});
