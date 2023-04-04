import { Col, Strip } from "@canonical/react-components";

import LoginForm from "@/components/LoginForm";
import NavigationBanner from "@/components/Navigation/NavigationBanner";

const Login: React.FC = () => {
  return (
    <div className="l-application">
      <header className="l-navigation-bar is-pinned">
        <div className="p-panel is-dark">
          <div className="p-panel__header">
            <NavigationBanner />
          </div>
        </div>
      </header>
      <main className="l-main">
        <div>
          <Strip element="section" includeCol={false} shallow>
            <Col size={12}>
              <LoginForm />
            </Col>
          </Strip>
        </div>
      </main>
    </div>
  );
};

export default Login;
