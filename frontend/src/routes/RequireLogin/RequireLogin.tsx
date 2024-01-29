import { useEffect } from "react";

import { useAuthContext } from "@/context";
import { Outlet, createSearchParams, useLocation, useNavigate } from "@/utils/router";

const RequireLogin = () => {
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

  return <Outlet />;
};

export default RequireLogin;
