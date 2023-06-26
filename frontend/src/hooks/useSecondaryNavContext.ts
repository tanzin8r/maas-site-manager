import type { SecondaryNavContext } from "@/components/SecondaryNavigation/SecondaryNavigation";
import { useLocation } from "@/router";

export default function useSecondaryNavContext() {
  let context: SecondaryNavContext = "settings";
  const { pathname } = useLocation();

  if (pathname.startsWith("/account")) {
    context = "account";
  } else if (pathname.startsWith("/settings")) {
    context = "settings";
  }

  return context;
}
