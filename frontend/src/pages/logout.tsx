import { useAuthContext } from "@/context";

const Logout = () => {
  const navigate = useNavigate();
  const { logout } = useAuthContext();

  useEffect(() => {
    logout(() => navigate("/login"));
  }, [navigate, logout]);

  return null;
};

export default Logout;
