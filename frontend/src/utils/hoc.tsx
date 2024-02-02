import { lazy } from "react";

import { ContentSection } from "@canonical/maas-react-components";
import { Notification } from "@canonical/react-components";
import { ErrorBoundary } from "react-error-boundary";

import ErrorMessage from "@/components/ErrorMessage";

export const lazyWithErrorBoundary = (importFunc: Parameters<typeof lazy>[0]) => {
  const LazyComponent = lazy(importFunc);
  return () => (
    <ErrorBoundary
      fallbackRender={({ error }) => (
        <ContentSection>
          <Notification severity="negative" title="Error">
            <ErrorMessage error={error} />
          </Notification>
        </ContentSection>
      )}
    >
      <LazyComponent />
    </ErrorBoundary>
  );
};
