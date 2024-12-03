import { RowSelectionContextProviders, useRowSelection } from "@/context/RowSelectionContext/RowSelectionContext";
import { userEvent, screen, render } from "@/utils/test-utils";

const renderTestComponent = ({ clearOnUnmount, currentPage }: { clearOnUnmount: boolean; currentPage: number }) => {
  const TestComponent = ({ clearOnUnmount, currentPage }: { clearOnUnmount: boolean; currentPage: number }) => {
    const { rowSelection, setRowSelection } = useRowSelection("sites", { clearOnUnmount, currentPage });
    const handleClick = () => {
      setRowSelection({ row: true });
    };
    return (
      <div>
        {rowSelection.row ? "Row selected" : "Row not selected"}
        <button onClick={handleClick}>Select row</button>
      </div>
    );
  };
  const { rerender } = render(
    <RowSelectionContextProviders>
      <TestComponent clearOnUnmount={clearOnUnmount} currentPage={currentPage} />
    </RowSelectionContextProviders>,
  );
  const unmount = () => {
    rerender(<RowSelectionContextProviders></RowSelectionContextProviders>);
  };
  const rerenderTestComponent = ({ clearOnUnmount, currentPage }: { clearOnUnmount: boolean; currentPage: number }) => {
    rerender(
      <RowSelectionContextProviders>
        <TestComponent clearOnUnmount={clearOnUnmount} currentPage={currentPage} />
      </RowSelectionContextProviders>,
    );
  };
  return { unmount, rerender: rerenderTestComponent };
};

it("can persist row selection on unmount", async () => {
  const { unmount, rerender } = renderTestComponent({ clearOnUnmount: false, currentPage: 1 });
  await userEvent.click(screen.getByText("Select row"));
  expect(screen.getByText("Row selected")).toBeInTheDocument();
  unmount();
  rerender({ clearOnUnmount: false, currentPage: 1 });
  expect(screen.getByText("Row selected")).toBeInTheDocument();
});

it("can clear row selection on unmount", async () => {
  const { unmount, rerender } = renderTestComponent({ clearOnUnmount: true, currentPage: 1 });
  await userEvent.click(screen.getByText("Select row"));
  expect(screen.getByText("Row selected")).toBeInTheDocument();
  unmount();
  rerender({ clearOnUnmount: true, currentPage: 1 });
  expect(screen.getByText("Row not selected")).toBeInTheDocument();
});

it("clears the row selection on page change", async () => {
  const { rerender } = renderTestComponent({ clearOnUnmount: false, currentPage: 1 });
  await userEvent.click(screen.getByText("Select row"));
  expect(screen.getByText("Row selected")).toBeInTheDocument();
  rerender({ clearOnUnmount: false, currentPage: 1 });
  expect(screen.getByText("Row selected")).toBeInTheDocument();
  rerender({ clearOnUnmount: false, currentPage: 2 });
  expect(screen.getByText("Row not selected")).toBeInTheDocument();
});
