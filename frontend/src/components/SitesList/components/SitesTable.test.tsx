import MockDate from "mockdate";
import timezoneMock from "timezone-mock";
import { vi } from "vitest";

import type { Site } from "../../../api/types";
import { sites, site } from "../../../mocks/factories";
import { render, screen, within } from "../../../test-utils";

import SitesTable from "./SitesTable";

beforeEach(() => {
  vi.useFakeTimers();
  timezoneMock.register("Etc/GMT");
});

afterEach(() => {
  timezoneMock.unregister();
  vi.useRealTimers();
});

it("displays an empty sites table", () => {
  render(<SitesTable data={[]} />);

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
});

it("displays rows with details for each site", () => {
  const items = sites().items as Site[];
  render(<SitesTable data={items} />);

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(items.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => expect(row).toHaveTextContent(new RegExp(items[i].name, "i")));
});

it("displays correct local time", () => {
  const date = new Date("2000-01-01T12:00:00Z");
  vi.setSystemTime(date);

  const item = site({ timezone: "CET" });
  render(<SitesTable data={[item]} />);

  expect(screen.getByRole("table", { name: /sites/i })).toBeInTheDocument();
  expect(screen.getByText(/13:00 \(local time\)/i)).toBeInTheDocument();
});
