import { Col, Row } from "@canonical/react-components";
import classNames from "classnames";
import { Outlet, useLocation } from "react-router-dom";

import "./MainLayout.scss";
import Navigation from "@/components/Navigation";
import TokensCreate from "@/pages/tokens/create";

const Aside = ({ children, isOpen }: { children: React.ReactNode; isOpen: boolean }) => (
  <aside className={classNames("l-aside", "is-maas-site-manager", { "is-collapsed": !isOpen })} id="aside-panel">
    <Row>
      <Col size={12}>{children}</Col>
    </Row>
  </aside>
);

const MainLayout: React.FC = () => {
  const { state, pathname } = useLocation();
  const hasSidebar = !!state?.sidebar;

  return (
    <div className="l-application">
      <Navigation />
      <main className="l-main is-maas-site-manager">
        <div className="row">
          <div className="col-12">
            <h1 className="u-hide">MAAS Site Manager</h1>
            <Outlet />
          </div>
        </div>
      </main>
      <Aside isOpen={hasSidebar}>{hasSidebar && pathname === "/tokens" ? <TokensCreate /> : null}</Aside>
    </div>
  );
};

export default MainLayout;
