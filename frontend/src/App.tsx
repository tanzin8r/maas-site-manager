import "@/styles/App.scss";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { RowSelectionContextProviders } from "./context/RowSelectionContext";
import { UserSelectionContextProvider } from "./context/UserSelectionContext";

import apiClient from "@/api";
import { AppLayoutContextProvider, AuthContextProvider } from "@/context";
import routes from "@/routes";
import { createBrowserRouter, RouterProvider } from "@/utils/router";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayoutContextProvider>
        <AuthContextProvider apiClient={apiClient}>
          <RowSelectionContextProviders>
            <UserSelectionContextProvider>
              <RouterProvider router={router} />
            </UserSelectionContextProvider>
          </RowSelectionContextProviders>
        </AuthContextProvider>
      </AppLayoutContextProvider>
    </QueryClientProvider>
  );
};

export default App;
