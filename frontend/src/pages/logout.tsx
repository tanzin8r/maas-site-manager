import { useAuthContext } from "@/context";
import { useNavigate } from "@/utils/router";

const Logout = () => {
  const navigate = useNavigate();
  const { logout } = useAuthContext();

  useEffect(() => {
    logout(() => navigate("/login"));
  }, [navigate, logout]);

  return null;
};

export default Logout;
