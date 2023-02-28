import { Outlet } from "react-router-dom";
import "./MainLayout.scss";

const MainLayout = () => (
  <div className="l-application">
    <main className="l-main is-maas-site-manager">
      <div className="row">
        <div className="col-12">
          <h1 className="u-hide">MAAS Site Manager</h1>
          <Outlet />
        </div>
      </div>
    </main>
  </div>
);

export default MainLayout;
