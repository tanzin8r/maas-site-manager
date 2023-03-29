import { createRoutesFromElements, Route, redirect } from "react-router-dom";

import MainLayout from "@/components/MainLayout";
import Requests from "@/pages/requests";
import SitesList from "@/pages/sites";
import Tokens from "@/pages/tokens/tokens";

export const routes = createRoutesFromElements(
  <Route element={<MainLayout />} path="/">
    {/*
          TODO: redirect to /login when unauthenticated
          https://warthogs.atlassian.net/browse/MAASENG-1450
      */}
    <Route index loader={() => redirect("sites")} />
    <Route path="login" />
    <Route path="logout" />
    <Route element={<SitesList />} path="sites" />
    <Route element={<Requests />} path="requests" />
    <Route element={<Tokens />} path="tokens" />
    <Route path="users" />
  </Route>,
);

export default routes;
