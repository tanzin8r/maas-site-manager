import type { ReactElement } from "react";
import React from "react";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { RenderOptions, RenderResult } from "@testing-library/react";
import { render } from "@testing-library/react";

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

const customRender: (ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) => RenderResult = (
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">,
) => render(ui, { wrapper: Providers, ...options });

export { screen, within, waitFor } from "@testing-library/react";
export { customRender as render };
export { Providers };
