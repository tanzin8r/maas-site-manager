import { createRoutesFromElements, Route, redirect } from "react-router-dom";

import RequireLogin from "./RequireLogin";

import MainLayout from "@/components/MainLayout";
import NotFound from "@/pages/404";
import Login from "@/pages/login";
import Logout from "@/pages/logout";
import Requests from "@/pages/requests";
import Settings from "@/pages/settings";
import SitesList from "@/pages/sites";
import Tokens from "@/pages/tokens/tokens";

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
    <Route index loader={() => redirect("sites")} />
    <Route element={<Logout />} path="logout" />
    <Route element={<Login />} path="login" />
    <Route
      element={
        <RequireLogin>
          <SitesList />
        </RequireLogin>
      }
      path="sites"
    />
    <Route
      element={
        <RequireLogin>
          <Settings />
        </RequireLogin>
      }
      path="settings"
    >
      <Route element={<RequireLogin />} index loader={() => redirect("tokens")} />
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
    </Route>
    <Route path="users" />
  </Route>,
);

export default routes;
