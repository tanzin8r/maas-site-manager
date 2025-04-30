import { rest } from "msw";

import UploadImage from "./UploadImage";

import { createMockUploadImageResolver } from "@/mocks/resolvers";
import { apiUrls } from "@/utils/test-urls";
import { fireEvent, render, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

// TODO: Update to support multiple files https://warthogs.atlassian.net/browse/MAASENG-2588
function createDataTransfer(file: File) {
  return {
    files: [file],
    items: [
      {
        kind: "file",
        type: file.type,
        getAsFile: () => file,
      },
    ],
    types: ["Files"],
  };
}

const mockServer = setupServer(rest.post(`${apiUrls.images}`, createMockUploadImageResolver()));

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("renders without crashing", () => {
  render(<UploadImage />);
  expect(screen.getByRole("heading", { name: "Upload image" })).toBeInTheDocument();
});

it("only shows the 'Base image' dropdown if the selected release is 'Custom'", async () => {
  render(<UploadImage />);

  expect(screen.queryByRole("combobox", { name: "Base image" })).not.toBeInTheDocument();

  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Release" }), "Custom");

  expect(screen.getByRole("combobox", { name: "Base image" })).toBeInTheDocument();
});

it("only allows letters, digits, hyphens, and underscores for 'Image ID'", async () => {
  render(<UploadImage />);

  const imageIdInput = screen.getByRole("textbox", { name: "Image ID" });

  await userEvent.type(imageIdInput, "This is definitely not valid.");
  await userEvent.tab();
  expect(screen.getByText("Image ID can only contain letters, digits, hyphens and underscores.")).toBeInTheDocument();

  await userEvent.clear(imageIdInput);
  await userEvent.type(imageIdInput, "a-valid-image-id_3");
  expect(
    screen.queryByText("Image ID can only contain letters, digits, hyphens and underscores."),
  ).not.toBeInTheDocument();
});

it("shows file type validation errors", async () => {
  render(<UploadImage />);

  const file = new File(["beepbop"], "beepbop.png", { type: "image/png" });

  fireEvent.drop(screen.getByRole("button", { name: "Drag and drop files here or click to upload" }), {
    dataTransfer: createDataTransfer(file),
  });

  await userEvent.tab();

  expect(screen.getByText("File type is invalid.")).toBeInTheDocument();
});

// this will be fixed in https://warthogs.atlassian.net/browse/MAASENG-4706
it.skip("shows errors after submission", async () => {
  mockServer.use(
    rest.post(`${apiUrls.images}`, (req, res, ctx) => {
      throw res(ctx.status(400));
    }),
  );

  render(<UploadImage />);

  await userEvent.type(screen.getByRole("textbox", { name: "Release title" }), "Kubuntu 24.10");
  await userEvent.type(screen.getByRole("textbox", { name: "Image ID" }), "kubuntu_24-10");
  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Release" }), "Custom");
  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Base image" }), "Ubuntu");
  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Architecture" }), "amd64");

  const file = new File(["kubuntu_24-10"], "kubuntu_24-10.tgz", { type: "application/gzip" });

  fireEvent.drop(screen.getByRole("button", { name: "Drag and drop files here or click to upload" }), {
    dataTransfer: createDataTransfer(file),
  });

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText("Error while uploading image")).toBeInTheDocument();
  });
});
