import { lazy } from "react";

import RequireLogin from "./RequireLogin";

import MainLayout from "@/components/MainLayout";
import { createRoutesFromElements, Route, redirect } from "@/utils/router";

const Logout = lazy(() => import("@/routes/logout"));
const Login = lazy(() => import("@/routes/login"));
const NotFound = lazy(() => import("@/routes/404"));
const Sites = lazy(() => import("@/routes/sites"));
const List = lazy(() => import("@/routes/sites/list"));
const Map = lazy(() => import("@/routes/sites/map"));
const ImagesList = lazy(() => import("@/components/ImagesList"));
const Settings = lazy(() => import("@/routes/settings"));
const Tokens = lazy(() => import("@/routes/tokens/tokens"));
const Requests = lazy(() => import("@/routes/requests"));
const Users = lazy(() => import("@/routes/users"));
const MapSettings = lazy(() => import("@/components/MapSettings"));
const ImageServer = lazy(() => import("@/routes/settings/images/server"));
const ImagesMaas = lazy(() => import("@/routes/settings/images/maas"));
const ImageTransfer = lazy(() => import("@/routes/settings/images/transfer"));
const Account = lazy(() => import("@/routes/account"));
const PersonalDetails = lazy(() => import("@/routes/personalDetails"));
const Password = lazy(() => import("@/routes/account/password"));

export const routes = createRoutesFromElements(
  <Route element={<MainLayout />} path="/">
    <Route element={<Logout />} path="logout" />
    <Route element={<Login />} path="login" />

    <Route element={<RequireLogin />}>
      <Route element={<NotFound />} path="*" />
      <Route index loader={() => redirect("/sites")} />
      <Route element={<Sites />} path="sites">
        <Route index loader={() => redirect("/sites/list")} />
        <Route element={<List />} index path="list" />
        <Route element={<Map />} index path="map" />
      </Route>
      <Route path="images">
        <Route index loader={() => redirect("/images/list")} />
        <Route element={<ImagesList />} index path="list" />
      </Route>
      <Route element={<Settings />} path="settings">
        <Route element={<RequireLogin />} index loader={() => redirect("/settings/tokens")} />
        <Route element={<Tokens />} path="tokens" />
        <Route element={<Requests />} path="requests" />
        <Route element={<Users />} path="users" />
        <Route element={<MapSettings />} path="map" />
        <Route path="images">
          <Route element={<RequireLogin />} index loader={() => redirect("/settings/images/server")} />
          <Route element={<ImageServer />} path="server" />
          <Route element={<ImagesMaas />} path="maas" />
          <Route element={<ImageTransfer />} path="transfer" />
        </Route>
      </Route>
      <Route element={<Account />} path="account">
        <Route element={<RequireLogin />} index loader={() => redirect("/account/details")} />
        <Route element={<PersonalDetails />} path="details" />
        <Route element={<Password />} path="password" />
      </Route>
    </Route>
  </Route>,
);

export default routes;
