import { createContext, useContext, useEffect, useState } from "react";

import type { OnChangeFn, RowSelectionState } from "@tanstack/react-table";
import type { AxiosInstance } from "axios";
import useLocalStorageState from "use-local-storage-state";

import type { LoginError } from "@/hooks/api";
import { useLoginMutation } from "@/hooks/api";

export const AppContext = createContext<{
  rowSelection: RowSelectionState;
  setRowSelection: OnChangeFn<RowSelectionState>;
  sidebar: "removeRegions" | "createToken" | null;
  setSidebar: (sidebar: "removeRegions" | "createToken" | null) => void;
}>({
  rowSelection: {},
  setRowSelection: () => ({}),
  sidebar: null,
  setSidebar: () => null,
});

export const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [sidebar, setSidebar] = useState<"removeRegions" | "createToken" | null>(null);

  return (
    <AppContext.Provider value={{ rowSelection, setRowSelection, sidebar, setSidebar }}>{children}</AppContext.Provider>
  );
};

type AuthStatus = "initial" | "authenticated" | "unauthorised";

interface AuthContextType {
  status: AuthStatus;
  setStatus: (status: AuthStatus) => void;
  setAuthToken: (token: string) => void;
  removeAuthToken: VoidFunction;
  login: ({ username, password }: { username: string; password: string }) => void;
  logout: (callback: VoidFunction) => void;
  isError: boolean;
  failureReason: LoginError | null;
}

export const AuthContext = createContext<AuthContextType>({
  status: "initial",
  setStatus: () => null,
  setAuthToken: () => null,
  removeAuthToken: () => null,
  login: () => null,
  logout: () => null,
  isError: false,
  failureReason: null,
});

export const AuthContextProvider = ({
  apiClient,
  children,
}: {
  apiClient: AxiosInstance;
  children: React.ReactNode;
}) => {
  const [authToken, setAuthToken, { removeItem: removeAuthToken }] = useLocalStorageState("jwtToken");
  const [status, setStatus] = useState<AuthStatus>("initial");
  const { mutateAsync, isError, failureReason } = useLoginMutation();

  useEffect(() => {
    if (!authToken) {
      setStatus("unauthorised");
    } else {
      setStatus("authenticated");
    }
  }, [apiClient, authToken]);

  useEffect(() => {
    if (authToken) {
      apiClient.interceptors.request.use(function (config) {
        if (authToken) {
          config.headers.Authorization = `Bearer ${authToken}`;
        }
        return config;
      });
    }
  }, [apiClient, authToken]);

  useEffect(() => {
    apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response.status === 401) {
          removeAuthToken();
        }
        return Promise.reject(error);
      },
    );
  }, [apiClient, removeAuthToken]);

  const login = async ({ username, password }: { username: string; password: string }) => {
    try {
      const response = await mutateAsync({ username, password });
      setAuthToken(response.access_token);
      setStatus("authenticated");
    } catch (error) {
      setStatus("unauthorised");
    }
  };

  const logout = (callback: VoidFunction) => {
    removeAuthToken();
    setStatus("unauthorised");
    callback();
  };

  return (
    <AuthContext.Provider
      value={{ status, setStatus, setAuthToken, removeAuthToken, login, logout, isError, failureReason }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
export const useAuthContext = () => useContext(AuthContext);
