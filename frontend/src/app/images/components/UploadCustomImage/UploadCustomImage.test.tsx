import { http, HttpResponse } from "msw";

import UploadCustomImage from "./UploadCustomImage";

import { imageResolvers } from "@/testing/resolvers/images";
import { apiUrls } from "@/utils/test-urls";
import { fireEvent, render, screen, setupServer, userEvent, waitFor } from "@/utils/test-utils";

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

const mockServer = setupServer(imageResolvers.uploadCustomImage.handler());

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
  render(<UploadCustomImage />);
  expect(screen.getByRole("heading", { name: "Upload custom image" })).toBeInTheDocument();
});

it("shows file type validation errors", async () => {
  render(<UploadCustomImage />);

  const file = new File(["beepbop"], "beepbop.png", { type: "image/png" });

  fireEvent.drop(screen.getByRole("button", { name: "Drag and drop files here or click to upload" }), {
    dataTransfer: createDataTransfer(file),
  });

  await userEvent.tab();

  expect(screen.getByText("File type is invalid.")).toBeInTheDocument();
});

it("shows errors after submission", async () => {
  mockServer.use(
    http.post(apiUrls.images, () => {
      return HttpResponse.json({ message: "screw you" }, { status: 400 });
    }),
  );

  render(<UploadCustomImage />);

  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Operating system" }), "Ubuntu");
  await userEvent.type(screen.getByRole("textbox", { name: "Release title" }), "25.04");
  await userEvent.type(screen.getByRole("textbox", { name: "Release codename" }), "plucky");
  await userEvent.selectOptions(screen.getByRole("combobox", { name: "Architecture" }), "amd64");

  const file = new File(["ubuntu_25-04"], "ubuntu_25-04.tgz", { type: "application/gzip" });

  fireEvent.drop(screen.getByRole("button", { name: "Drag and drop files here or click to upload" }), {
    dataTransfer: createDataTransfer(file),
  });

  await userEvent.click(screen.getByRole("button", { name: "Save" }));

  await waitFor(() => {
    expect(screen.getByText("Error while uploading image")).toBeInTheDocument();
  });
});
