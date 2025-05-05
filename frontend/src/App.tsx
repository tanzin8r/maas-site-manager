import "@/styles/App.scss";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { BootSourceContextProvider } from "./context/BootSourceContext";
import { RowSelectionContextProviders } from "./context/RowSelectionContext";
import { SiteDetailsContextProvider } from "./context/SiteDetailsContext";
import { UserSelectionContextProvider } from "./context/UserSelectionContext";

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
        <AuthContextProvider>
          <RowSelectionContextProviders>
            <UserSelectionContextProvider>
              <SiteDetailsContextProvider>
                <BootSourceContextProvider>
                  <RouterProvider router={router} />
                </BootSourceContextProvider>
              </SiteDetailsContextProvider>
            </UserSelectionContextProvider>
          </RowSelectionContextProviders>
        </AuthContextProvider>
      </AppLayoutContextProvider>
    </QueryClientProvider>
  );
};

export default App;
