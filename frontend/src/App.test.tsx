import App from "./App";
import { render, screen } from "./test-utils";

describe("App", () => {
  it("renders headline", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: /MAAS Site Manager/i })).toBeInTheDocument();
  });
});
