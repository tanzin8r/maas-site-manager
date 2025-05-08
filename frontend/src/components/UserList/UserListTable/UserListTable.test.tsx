import { setupServer } from "msw/node";

import UserListTable from "./UserListTable";

import { userFactory, usersQueryResultFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import { renderWithMemoryRouter, screen, within } from "@/utils/test-utils";

const mockServer = setupServer(usersResolvers.getCurrentUser.handler(userFactory.build()));

beforeAll(() => {
  mockServer.listen();
});
beforeEach(() => {
  vi.useFakeTimers();
});
afterEach(() => {
  vi.useRealTimers();
  mockServer.resetHandlers();
});
afterAll(() => {
  mockServer.close();
});

it("renders an empty users table", () => {
  renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build()}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  expect(screen.getByRole("table", { name: "users" })).toBeInTheDocument();
  expect(screen.getAllByRole("row")).toHaveLength(1); // Only header row should be there
});

it("renders a spinner while loading", () => {
  renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build()}
      error={null}
      isPending={true}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  expect(screen.getByText(/Loading/i)).toBeInTheDocument();
});

it("shows errors if present", () => {
  const errorMessage = "There has been an error!";
  renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build()}
      error={{ error: { message: errorMessage } }}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  expect(screen.getByText(errorMessage)).toBeInTheDocument();
});

it("renders rows with details for each user", () => {
  const items = userFactory.buildList(5);
  renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build({ items, total: 1, page: 1, size: 1 })}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  expect(screen.getByRole("table", { name: "users" })).toBeInTheDocument();

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(items.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => {
      expect(within(row).getAllByRole("cell")[0]).toHaveTextContent(items[i].username); // Username should be displayed by default
      expect(within(row).getAllByRole("cell")[1]).toHaveTextContent(items[i].email);

      // Check that the user role is being displayed correctly
      const role = items[i].is_admin ? "Admin" : "User";

      expect(within(row).getAllByRole("cell")[2]).toHaveTextContent(role);
    });
});

it("renders correctly paginated results", () => {
  const pageLength = 50;
  const items = userFactory.buildList(pageLength);

  renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build({ items, total: 100, page: 1, size: pageLength })}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(pageLength);
});

it("displays the correct sort direction label", () => {
  const items = userFactory.buildList(2);
  const { rerender } = renderWithMemoryRouter(
    <UserListTable
      data={usersQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[]}
    />,
  );

  const emailDescending = ["columnheader", { name: /Email descending/i }] as const;
  const emailAscending = ["columnheader", { name: /Email ascending/i }] as const;

  expect(screen.getByRole("columnheader", { name: /Email/i })).toBeInTheDocument();
  expect(screen.queryByRole(...emailAscending)).not.toBeInTheDocument();
  expect(screen.queryByRole(...emailDescending)).not.toBeInTheDocument();

  // Sort by email descending
  rerender(
    <UserListTable
      data={usersQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[{ id: "email", desc: true }]}
    />,
  );

  expect(screen.getByRole(...emailDescending)).toBeInTheDocument();
  expect(screen.queryByRole(...emailAscending)).not.toBeInTheDocument();

  // Sort by email ascending
  rerender(
    <UserListTable
      data={usersQueryResultFactory.build({ items, total: 2, page: 1, size: 10 })}
      error={null}
      isPending={false}
      setSorting={vi.fn()}
      sorting={[{ id: "email", desc: false }]}
    />,
  );

  expect(screen.getByRole(...emailAscending)).toBeInTheDocument();
  expect(screen.queryByRole(...emailDescending)).not.toBeInTheDocument();
});
