import MainLayout from "./MainLayout";

import { renderWithMemoryRouter, screen, waitFor } from "@/utils/test-utils";

it("renders header", async () => {
  renderWithMemoryRouter(<MainLayout />);

  await waitFor(() =>
    expect(screen.getByRole("heading", { level: 1, name: /MAAS Site Manager/i })).toBeInTheDocument(),
  );
});
