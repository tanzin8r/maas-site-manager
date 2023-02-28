import { createBrowserRouter, createRoutesFromElements, Route } from "react-router-dom";

import MainLayout from "./components/MainLayout";
import SitesList from "./components/SitesList/SitesList";

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<MainLayout />} path="/">
      <Route path="login" />
      <Route path="logout" />
      <Route element={<SitesList />} path="sites" />
      <Route path="requests" />
      <Route path="tokens" />
      <Route path="users" />
    </Route>,
  ),
);

export default router;
