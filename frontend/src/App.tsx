import "./App.scss";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { RowSelectionContextProviders } from "./context/RowSelectionContext";

import apiClient from "@/api";
import { AppContextProvider, AuthContextProvider } from "@/context";
import { createBrowserRouter, RouterProvider } from "@/router";
import routes from "@/routes";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContextProvider>
        <AuthContextProvider apiClient={apiClient}>
          <RowSelectionContextProviders>
            <RouterProvider router={router} />
          </RowSelectionContextProviders>
        </AuthContextProvider>
      </AppContextProvider>
    </QueryClientProvider>
  );
};

export default App;
