import { useEffect } from "react";

import { createSearchParams, useLocation, useNavigate } from "react-router-dom";

import { useAuthContext } from "@/context";

const RequireLogin = ({ children }: { children?: React.ReactNode }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { status } = useAuthContext();

  useEffect(() => {
    if (status === "unauthorised") {
      navigate({
        pathname: "/login",
        search: `?${createSearchParams({ redirectTo: location.pathname })}`,
      });
    }
  }, [location, navigate, status]);

  if (status !== "authenticated") {
    return null;
  }

  return <>{children}</>;
};

export default RequireLogin;
