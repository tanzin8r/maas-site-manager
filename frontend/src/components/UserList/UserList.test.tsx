import UserList from "./UserList";

import { userFactory } from "@/mocks/factories";
import { usersResolvers } from "@/testing/resolvers/users";
import * as router from "@/utils/router";
import {
  renderWithMemoryRouter,
  screen,
  setupServer,
  userEvent,
  waitFor,
  waitForLoadingToFinish,
  within,
} from "@/utils/test-utils";

const userWithoutFullName = userFactory.build({ full_name: "" });
const users = [...userFactory.buildList(2), userWithoutFullName];
const mockServer = setupServer(
  usersResolvers.listUsers.handler(users),
  usersResolvers.getCurrentUser.handler(users[0]),
);

beforeAll(() => {
  mockServer.listen();
});

afterEach(() => {
  mockServer.resetHandlers();
});

afterAll(() => {
  mockServer.close();
});

it("renders a populated user table", async () => {
  renderWithMemoryRouter(<UserList />);

  expect(screen.getByRole("table", { name: "users" })).toBeInTheDocument();

  await waitForLoadingToFinish();
  await waitFor(() => expect(screen.getAllByRole("rowgroup")).toHaveLength(2));
  const tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(users.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => {
      expect(within(row).getAllByRole("cell")[0]).toHaveTextContent(users[i].username); // Username should be displayed by default
      expect(within(row).getAllByRole("cell")[1]).toHaveTextContent(users[i].email);

      // Check that the user role is being displayed correctly
      const role = users[i].is_admin ? "Admin" : "User";

      expect(within(row).getAllByRole("cell")[2]).toHaveTextContent(role);
    });
});

it("can switch between username and full name display", async () => {
  renderWithMemoryRouter(<UserList />);

  await waitForLoadingToFinish();
  await waitFor(() => expect(screen.getAllByRole("rowgroup")).toHaveLength(2));
  let tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(users.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => {
      expect(within(row).getAllByRole("cell")[0]).toHaveTextContent(users[i].username); // Username should be displayed by default
    });

  await userEvent.click(screen.getByRole("button", { name: "Full name" }));

  tableBody = screen.getAllByRole("rowgroup")[1];
  expect(within(tableBody).getAllByRole("row")).toHaveLength(users.length);
  within(tableBody)
    .getAllByRole("row")
    .forEach((row, i) => {
      // If a full name is set, it should be displayed. Otherwise, display a dash
      const fullName = users[i].full_name as string;
      expect(within(row).getAllByRole("cell")[0]).toHaveTextContent(fullName ? fullName : "—");
    });
});

it("displays a pagination bar with the table", async () => {
  renderWithMemoryRouter(<UserList />);

  await waitFor(() => {
    expect(screen.getByText(/Showing 3 out of 3 users/i)).toBeInTheDocument();
  });
  expect(screen.getByRole("button", { name: /next page/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /previous page/i })).toBeInTheDocument();
});

it("displays a sort direction label", async () => {
  renderWithMemoryRouter(<UserList />);

  const emailDescending = ["columnheader", { name: /Email descending/i }] as const;
  const emailAscending = ["columnheader", { name: /Email ascending/i }] as const;

  expect(screen.getByRole("columnheader", { name: /Email/i })).toBeInTheDocument();
  expect(screen.queryByRole(...emailDescending)).not.toBeInTheDocument();
  expect(screen.queryByRole(...emailAscending)).not.toBeInTheDocument();

  await userEvent.click(screen.getByRole("columnheader", { name: /Email/i }));

  expect(screen.getByRole(...emailDescending)).toBeInTheDocument();
  expect(screen.queryByRole(...emailAscending)).not.toBeInTheDocument();

  await userEvent.click(screen.getByRole("columnheader", { name: /Email/i }));

  expect(screen.getByRole(...emailAscending)).toBeInTheDocument();
  expect(screen.queryByRole(...emailDescending)).not.toBeInTheDocument();
});

it("redirects to personal details if a user tries to edit themselves", async () => {
  const navigate = vi.fn();
  vi.spyOn(router, "useNavigate").mockImplementation(() => navigate);
  renderWithMemoryRouter(<UserList />, { initialEntries: [{ pathname: "/settings/users", key: "testkey" }] });

  // Wait for table to load
  await waitFor(() => {
    expect(screen.getByRole("button", { name: `Edit ${users[0].username}` })).toBeInTheDocument();
  });

  await userEvent.click(screen.getByRole("button", { name: `Edit ${users[0].username}` }));

  expect(navigate).toHaveBeenCalledWith("/account/details");
});

it("displays a tooltip if a user tries to delete themselves", async () => {
  renderWithMemoryRouter(<UserList />);

  // Wait for table to render
  await waitFor(() => {
    expect(screen.getByRole("button", { name: `Delete ${users[0].username}` })).toBeInTheDocument();
  });

  await userEvent.click(screen.getByRole("button", { name: `Delete ${users[0].username}` }));

  expect(screen.getByRole("tooltip", { name: "You cannot delete your own user." })).toBeInTheDocument();
});
