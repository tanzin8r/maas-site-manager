import type { ReactElement } from "react";
import * as React from "react";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { RenderOptions, RenderResult } from "@testing-library/react";
import { screen, render } from "@testing-library/react";
import type { MemoryRouterProps } from "react-router-dom";
import { MemoryRouter } from "react-router-dom";

import { AppContextProvider, AuthContextProvider } from "./context";

import apiClient from "@/api";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // in tests any unsuccessful query should fail immediately without retrying
      retry: false,
    },
  },
});

const Providers = ({ children }: { children: React.ReactNode }) => {
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
};

const makeProvidersWithMemoryRouter =
  (memoryRouterProps: MemoryRouterProps) =>
  ({ children }: { children: React.ReactNode }) => {
    return (
      <Providers>
        <MemoryRouter {...memoryRouterProps}>
          <AppContextProvider>
            <AuthContextProvider apiClient={apiClient}>{children}</AuthContextProvider>
          </AppContextProvider>
        </MemoryRouter>
      </Providers>
    );
  };

const customRender: (ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) => RenderResult = (
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">,
) => render(ui, { wrapper: Providers, ...options });

interface MemoryRenderOptions extends MemoryRouterProps, Omit<RenderOptions, "wrapper"> {}
const renderWithMemoryRouter = (ui: ReactElement, options?: MemoryRenderOptions) => {
  const { basename, initialEntries, initialIndex } = options || {};
  const Providers = makeProvidersWithMemoryRouter({ basename, initialEntries, initialIndex });
  return render(ui, { wrapper: Providers, ...options });
};

const getByTextContent = (text: string | RegExp) => {
  return screen.getByText((_, element) => {
    const hasText = (element: Element | null) => {
      if (element) {
        if (text instanceof RegExp && element.textContent) {
          return text.test(element.textContent);
        } else {
          return element.textContent === text;
        }
      } else {
        return false;
      }
    };
    const elementHasText = hasText(element);
    const childrenDontHaveText = Array.from(element?.children || []).every((child) => !hasText(child));
    return elementHasText && childrenDontHaveText;
  });
};

export { screen, within, waitFor, act } from "@testing-library/react";
export { customRender as render };
export { renderHook, act as hookAct } from "@testing-library/react-hooks";
export { default as userEvent } from "@testing-library/user-event";
export { renderWithMemoryRouter };
export { Providers };
export { setupServer } from "msw/node";
export { getByTextContent };
