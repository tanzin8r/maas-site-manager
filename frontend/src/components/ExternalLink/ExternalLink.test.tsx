import ExternalLink from "./ExternalLink";

import { renderWithMemoryRouter, screen, userEvent } from "@/utils/test-utils";

test("renders with correct attributes", () => {
  renderWithMemoryRouter(<ExternalLink to="https://example.com">Example Link</ExternalLink>);

  const linkElement = screen.getByText(/example link/i);
  expect(linkElement).toBeInTheDocument();
  expect(linkElement).toHaveAttribute("rel", "noreferrer noopener");
  expect(linkElement).toHaveAttribute("href", "https://example.com");
  expect(linkElement).toHaveAttribute("target", "_blank");
});

test("calls onClick handler when pressed", async () => {
  const handleClick = vi.fn();

  renderWithMemoryRouter(
    <ExternalLink onClick={handleClick} to="https://example.com">
      Example Link
    </ExternalLink>,
  );

  const linkElement = screen.getByText(/example link/i);
  await userEvent.click(linkElement);

  expect(handleClick).toHaveBeenCalled();
});
