import { http, HttpResponse } from "msw";

import type { User, UsersPostRequest } from "@/api";
import { type SortDirection, type UserSortKey } from "@/api/handlers";
import { userFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockUsers = userFactory.buildList(155);
const usersResolvers = {
  listUsers: {
    resolved: false,
    handler: (data: User[] = mockUsers) => {
      return http.get(apiUrls.users, ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));

        // sort items
        const items = [...data];
        const sortBy = searchParams.get("sortBy");
        if (sortBy) {
          const [field, order] = sortBy.split("-") as [UserSortKey, SortDirection];
          items.sort((a, b) => {
            if (order === "asc") {
              return a[field] > b[field] ? 1 : -1;
            }
            return a[field] < b[field] ? 1 : -1;
          });
        }

        const itemsPage = items.slice((page - 1) * size, page * size);

        const response = {
          items: itemsPage,
          page,
          total: data.length,
        };
        usersResolvers.listUsers.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  getUser: {
    resolved: false,
    handler: (data: User[] = mockUsers) => {
      return http.get(`${apiUrls.users}/:id`, ({ params }) => {
        usersResolvers.getUser.resolved = true;
        const id = params.id;
        if (id === "me") {
          const user = userFactory.build(
            data ? data[0] : { username: "admin", full_name: "MAAS Admin", email: "admin@example.com" },
          );
          return HttpResponse.json(user);
        }
        const user = data.find((user) => user.id === Number(id));
        return user ? HttpResponse.json(user) : HttpResponse.error();
      });
    },
  },
  getCurrentUser: {
    resolved: false,
    handler: (data: User = mockUsers[0]) => {
      usersResolvers.getCurrentUser.resolved = true;
      return http.get(apiUrls.currentUser, () => {
        const user = userFactory.build(
          data ? data : { username: "admin", full_name: "MAAS Admin", email: "admin@example.com" },
        );
        return HttpResponse.json(user);
      });
    },
  },
  updateUser: {
    resolved: false,
    handler: () => {
      return http.patch(`${apiUrls.users}/:id`, async ({ request, params }) => {
        const { full_name, username, email, is_admin } = (await request.json()) as UsersPostRequest;
        const id = params.id;
        const user = { id: Number(id), full_name, username, email, is_admin };
        usersResolvers.updateUser.resolved = true;
        return HttpResponse.json(user);
      });
    },
  },
  updateCurrentUser: {
    resolved: false,
    handler: () => {
      return http.patch(apiUrls.currentUser, async () => {
        usersResolvers.updateCurrentUser.resolved = true;
        return new HttpResponse(null, { status: 200 });
      });
    },
  },
  updateCurrentUserPassword: {
    resolved: false,
    handler: () => {
      return http.patch(`${apiUrls.currentUser}/password`, async () => {
        usersResolvers.updateCurrentUserPassword.resolved = true;
        return new HttpResponse(null, { status: 200 });
      });
    },
  },
  createUser: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.users, async ({ request }) => {
        const { username, full_name, email, is_admin } = (await request.json()) as UsersPostRequest;
        const newUser = userFactory.build({ username, full_name, email, is_admin });
        usersResolvers.createUser.resolved = true;
        return new HttpResponse(JSON.stringify(newUser), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        });
      });
    },
  },
  deleteUser: {
    resolved: false,
    handler: () => {
      return http.delete(`${apiUrls.users}/:id`, async () => {
        usersResolvers.deleteUser.resolved = true;
        return new HttpResponse(null, { status: 204 });
      });
    },
  },
};
export { usersResolvers };
