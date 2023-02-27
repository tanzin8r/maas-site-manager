import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
  redirect,
} from "react-router-dom";
import MainLayout from "./components/MainLayout";
import SitesList from "./components/SitesList/SitesList";

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route path="login" />
      <Route path="logout" />
      <Route path="sites" element={<SitesList />} />
      <Route path="requests" />
      <Route path="tokens" />
      <Route path="users" />
    </Route>
  )
);

export default router;
