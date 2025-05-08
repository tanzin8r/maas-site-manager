import DeleteImagesContainer, { DeleteImages } from "./DeleteImages";

import * as context from "@/context";
import { imagesResolvers } from "@/testing/resolvers/images";
import { getByTextContent, render, screen, setupServer, userEvent } from "@/utils/test-utils";

const mockServer = setupServer(imagesResolvers.deleteImages.handler());

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("displays delete confirmation", () => {
  render(<DeleteImages count={2} onCancel={vi.fn()} onDelete={vi.fn()} />);
  expect(getByTextContent(new RegExp("Are you sure you want to delete 2 images?", "s"))).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Delete 2 images" })).toBeInTheDocument();
});

it("can display an error message", () => {
  render(<DeleteImages count={2} error={Error("Uh oh!")} onCancel={vi.fn()} onDelete={vi.fn()} />);
  expect(screen.getByText("Uh oh!")).toBeInTheDocument();
});

it("calls a function on delete", async () => {
  const handleDelete = vi.fn();
  render(<DeleteImages count={2} onCancel={vi.fn()} onDelete={handleDelete} />);

  await userEvent.click(screen.getByRole("button", { name: /Delete/i }));

  expect(handleDelete).toHaveBeenCalledTimes(1);
});

it("calls a function on cancel", async () => {
  const handleCancel = vi.fn();
  render(<DeleteImages count={2} onCancel={handleCancel} onDelete={vi.fn()} />);

  await userEvent.click(screen.getByRole("button", { name: /Cancel/i }));

  expect(handleCancel).toHaveBeenCalledTimes(1);
});

it("clears row selection on delete", async () => {
  const clearRowSelection = vi.fn();
  vi.spyOn(context, "useRowSelection").mockImplementation(() => ({
    rowSelection: { "1": true, "2": true },
    setRowSelection: vi.fn(),
    clearRowSelection,
  }));

  render(<DeleteImagesContainer />);

  expect(getByTextContent(/Are you sure you want to delete 2 images/i)).toBeInTheDocument();

  await userEvent.click(screen.getByRole("button", { name: /Delete/i }));

  expect(clearRowSelection).toHaveBeenCalled();

  vi.restoreAllMocks();
});
