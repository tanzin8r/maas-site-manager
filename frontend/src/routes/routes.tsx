import { createRoutesFromElements, Route, redirect } from "react-router-dom";

import RequireLogin from "./RequireLogin";

import MainLayout from "@/components/MainLayout";
import Login from "@/pages/login";
import Logout from "@/pages/logout";
import Requests from "@/pages/requests";
import SitesList from "@/pages/sites";
import Tokens from "@/pages/tokens/tokens";

export const routes = createRoutesFromElements(
  <Route element={<MainLayout />} path="/">
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
          <Requests />
        </RequireLogin>
      }
      path="requests"
    />
    <Route
      element={
        <RequireLogin>
          <Tokens />
        </RequireLogin>
      }
      path="tokens"
    />
    <Route path="users" />
  </Route>,
);

export default routes;
