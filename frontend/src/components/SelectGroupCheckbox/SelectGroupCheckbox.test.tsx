import type { Row } from "@tanstack/react-table";

import SelectGroupCheckbox from "./SelectGroupCheckbox";

import type { Image } from "@/api";
import { imageFactory } from "@/mocks/factories";
import { render, userEvent, screen } from "@/utils/test-utils";

const renderSelectGroupCheckbox = (rowProps: Partial<Row<Image>> = {}) => {
  const mockRow: Row<Image> = Object.assign(
    {
      getIsSelected: vi.fn(() => false),
      getIsAllSubRowsSelected: vi.fn(() => false),
      getIsSomeSelected: vi.fn(() => false),
      getCanSelect: vi.fn(() => true),
      getIsGrouped: vi.fn(() => true),
      toggleSelected: vi.fn(),
      subRows: imageFactory.buildList(2).map((image) => ({ toggleSelected: vi.fn(), ...image })),
      original: imageFactory.build({ name: "Ubuntu" }),
    },
    rowProps,
  );
  return { ...render(<SelectGroupCheckbox row={mockRow} />), ...mockRow };
};

it("renders with correct accessible name", () => {
  renderSelectGroupCheckbox();
  expect(screen.getByRole("checkbox")).toHaveAccessibleName("Ubuntu");
});

it("is enabled when row can be selected", () => {
  renderSelectGroupCheckbox({ getCanSelect: vi.fn(() => true) });
  expect(screen.getByRole("checkbox")).toBeEnabled();
});

it("is disabled when row cannot be selected", () => {
  renderSelectGroupCheckbox({ getCanSelect: vi.fn(() => false) });
  expect(screen.getByRole("checkbox")).toBeDisabled();
});

it("toggles selection state on click", async () => {
  const { subRows, toggleSelected } = renderSelectGroupCheckbox();
  await userEvent.click(screen.getByRole("checkbox"));
  expect(toggleSelected).toHaveBeenCalledWith(true);
  expect(subRows[0].toggleSelected).toHaveBeenCalledWith(true);
  expect(subRows[1].toggleSelected).toHaveBeenCalledWith(true);
});

it("sets mixed state correctly", () => {
  renderSelectGroupCheckbox({ getIsSomeSelected: () => true });
  expect(screen.getByRole("checkbox")).toHaveAttribute("aria-checked", "mixed");
});
