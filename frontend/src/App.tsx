import "@/styles/App.scss";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { RowSelectionContextProviders } from "./context/RowSelectionContext";
import { SiteDetailsContextProvider } from "./context/SiteDetailsContext";
import { UserSelectionContextProvider } from "./context/UserSelectionContext";

import apiClient from "@/api";
import { basename } from "@/constants";
import { AppLayoutContextProvider, AuthContextProvider } from "@/context";
import routes from "@/routes";
import { createBrowserRouter, RouterProvider } from "@/utils/router";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes, { basename });

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayoutContextProvider>
        <AuthContextProvider apiClient={apiClient}>
          <RowSelectionContextProviders>
            <UserSelectionContextProvider>
              <SiteDetailsContextProvider>
                <RouterProvider router={router} />
              </SiteDetailsContextProvider>
            </UserSelectionContextProvider>
          </RowSelectionContextProviders>
        </AuthContextProvider>
      </AppLayoutContextProvider>
    </QueryClientProvider>
  );
};

export default App;
