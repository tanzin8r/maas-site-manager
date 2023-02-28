import type { ReactElement } from "react";
import React from "react";

import type { RenderOptions, RenderResult } from "@testing-library/react";
import { render } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "react-query";

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

export * from "@testing-library/react";
export { customRender as render };
export { Providers };
