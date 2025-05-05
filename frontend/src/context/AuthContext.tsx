import type { Reducer } from "react";
import React, { createContext, useContext, useReducer } from "react";

import useLocalStorageState from "use-local-storage-state";

import type { MutationErrorResponse } from "@/api";
import { OpenAPI } from "@/api/client";
import { useLogin } from "@/api/query/auth";
import type { PostV1LoginPostData } from "@/apiclient";
import { client } from "@/apiclient/client.gen";
type AuthStatus = "initial" | "authenticated" | "unauthorised";

interface AuthContextType {
  status: AuthStatus;
  login: ({ username, password }: Pick<PostV1LoginPostData["body"], "username" | "password">) => void;
  logout: () => Promise<void>;
  isError: boolean;
  error: MutationErrorResponse | null;
}

export const AuthContext = createContext<AuthContextType>({
  status: "initial",
  login: () => null,
  logout: () => new Promise(() => {}),
  isError: false,
  error: null,
});

export const actionTypes = {
  LOGIN_SUCCESS: "LOGIN_SUCCESS",
  LOGIN_ERROR: "LOGIN_ERROR",
  LOGOUT: "LOGOUT",
} as const;

const status = {
  AUTHENTICATED: "authenticated",
  UNAUTHORISED: "unauthorised",
} as const;

type Status = (typeof status)[keyof typeof status];
type ActionType = (typeof actionTypes)[keyof typeof actionTypes];
type AuthToken = string | null;
type AuthState = {
  authToken: AuthToken;
  status: Status;
};
type AuthAction =
  | {
      type: typeof actionTypes.LOGIN_SUCCESS;
      payload: AuthToken;
    }
  | {
      type: Exclude<ActionType, "LOGIN_SUCCESS">;
    };

const authReducer: Reducer<AuthState, AuthAction> = (state, action) => {
  switch (action.type) {
    case actionTypes.LOGIN_SUCCESS:
      return { ...state, status: "authenticated", authToken: action.payload };
    case actionTypes.LOGIN_ERROR:
      return { ...state, status: "unauthorised", authToken: null };
    case actionTypes.LOGOUT:
      return { ...state, status: "unauthorised", authToken: null };
    default:
      return state;
  }
};

export const AuthContextProvider = ({ children }: { children: React.ReactNode }) => {
  const [persistedAuthToken, setPersistedAuthToken] = useLocalStorageState<string>("jwtToken");
  const removePersistedAuthToken = useCallback(() => {
    localStorage.removeItem("jwtToken");
  }, []);

  const loginQuery = useLogin();

  const initialState: AuthState = {
    authToken: persistedAuthToken ? persistedAuthToken : null,
    status: persistedAuthToken ? "authenticated" : "unauthorised",
  };

  const clearAuthToken = useCallback(() => {
    OpenAPI.TOKEN = undefined;
    removePersistedAuthToken();
  }, [removePersistedAuthToken]);

  const updateAuthToken = useCallback(
    (authToken: AuthToken) => {
      if (authToken) {
        setPersistedAuthToken(authToken);
        OpenAPI.TOKEN = authToken;
      }
    },
    [setPersistedAuthToken],
  );
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Add a response interceptor to handle logout on 401 status
    client.instance.interceptors.response.use(
      function (response) {
        return response;
      },
      function (error) {
        if (error?.status === 401) {
          dispatch({ type: actionTypes.LOGOUT });
          clearAuthToken();
        }
        return Promise.reject(error);
      },
    );
  }, [clearAuthToken]);

  const login = async ({ username, password }: { username: string; password: string }) => {
    try {
      if (!username || !password) {
        throw Error("Missing required fields");
      }
      const response = await loginQuery.mutateAsync({ body: { username, password } });
      updateAuthToken(response.access_token);
      dispatch({ type: actionTypes.LOGIN_SUCCESS, payload: response.access_token });
    } catch (error) {
      dispatch({ type: actionTypes.LOGIN_ERROR });
    }
  };

  const logout = (): Promise<void> =>
    new Promise((resolve) => {
      clearAuthToken();
      dispatch({ type: actionTypes.LOGOUT });
      resolve();
    });

  return (
    <AuthContext.Provider
      value={{
        status: state.status,
        login,
        logout,
        isError: loginQuery.isError,
        error: loginQuery.error as MutationErrorResponse | null,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => useContext(AuthContext);
