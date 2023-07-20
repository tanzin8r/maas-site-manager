import RequireLogin from "./RequireLogin";

import MainLayout from "@/components/MainLayout";
import NotFound from "@/pages/404";
import Account from "@/pages/account";
import Password from "@/pages/account/password";
import Login from "@/pages/login";
import Logout from "@/pages/logout";
import PersonalDetails from "@/pages/personalDetails";
import Requests from "@/pages/requests";
import Settings from "@/pages/settings";
import Sites from "@/pages/sites";
import List from "@/pages/sites/list";
import Map from "@/pages/sites/map";
import Tokens from "@/pages/tokens/tokens";
import Users from "@/pages/users";
import { createRoutesFromElements, Route, redirect } from "@/router";

export const routes = createRoutesFromElements(
  <Route element={<MainLayout />} path="/">
    <Route
      element={
        <RequireLogin>
          <NotFound />
        </RequireLogin>
      }
      path="*"
    />
    <Route index loader={() => redirect("/sites")} />
    <Route element={<Logout />} path="logout" />
    <Route element={<Login />} path="login" />
    <Route
      element={
        <RequireLogin>
          <Sites />
        </RequireLogin>
      }
      path="sites"
    >
      <Route index loader={() => redirect("/sites/list")} />
      <Route
        element={
          <RequireLogin>
            <List />
          </RequireLogin>
        }
        index
        path="list"
      />
      <Route
        element={
          <RequireLogin>
            <Map />
          </RequireLogin>
        }
        index
        path="map"
      />
    </Route>
    <Route
      element={
        <RequireLogin>
          <Settings />
        </RequireLogin>
      }
      path="settings"
    >
      <Route element={<RequireLogin />} index loader={() => redirect("/settings/tokens")} />
      <Route
        element={
          <RequireLogin>
            <Tokens />
          </RequireLogin>
        }
        path="tokens"
      />
      <Route
        element={
          <RequireLogin>
            <Requests />
          </RequireLogin>
        }
        path="requests"
      />
      <Route
        element={
          <RequireLogin>
            <Users />
          </RequireLogin>
        }
        path="users"
      />
    </Route>
    <Route
      element={
        <RequireLogin>
          <Account />
        </RequireLogin>
      }
      path="account"
    >
      <Route element={<RequireLogin />} index loader={() => redirect("/account/details")} />
      <Route
        element={
          <RequireLogin>
            <PersonalDetails />
          </RequireLogin>
        }
        path="details"
      />

      <Route
        element={
          <RequireLogin>
            <Password />
          </RequireLogin>
        }
        path="password"
      />
    </Route>
  </Route>,
);

export default routes;
