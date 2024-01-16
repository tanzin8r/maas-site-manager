import RequireLogin from "./RequireLogin";

import ImagesList from "@/components/ImagesList";
import MainLayout from "@/components/MainLayout";
import MapSettings from "@/components/MapSettings";
import NotFound from "@/routes/404";
import Account from "@/routes/account";
import Password from "@/routes/account/password";
import Login from "@/routes/login";
import Logout from "@/routes/logout";
import PersonalDetails from "@/routes/personalDetails";
import Requests from "@/routes/requests";
import Settings from "@/routes/settings";
import Sites from "@/routes/sites";
import List from "@/routes/sites/list";
import Map from "@/routes/sites/map";
import Tokens from "@/routes/tokens/tokens";
import Users from "@/routes/users";
import { createRoutesFromElements, Route, redirect } from "@/utils/router";

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

    <Route path="images">
      <Route index loader={() => redirect("/images/list")} />
      <Route
        element={
          <RequireLogin>
            <ImagesList />
          </RequireLogin>
        }
        index
        path="list"
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
      <Route
        element={
          <RequireLogin>
            <MapSettings />
          </RequireLogin>
        }
        path="map"
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
