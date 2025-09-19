import { useAuthContext } from "@/app/context";
import { useNavigate } from "@/utils/router";

const Logout = () => {
  const navigate = useNavigate();
  const { logout } = useAuthContext();

  logout().then(() => navigate("/login"));

  return null;
};

export default Logout;
