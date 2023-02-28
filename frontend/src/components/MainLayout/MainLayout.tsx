import { Outlet } from "react-router-dom";

const MainLayout: React.FC = () => (
  <div className="l-application">
    <main className="l-main">
      <div className="row">
        <div className="col-12">
          <h1>MAAS Site Manager</h1>
          <Outlet />
        </div>
      </div>
    </main>
  </div>
);

export default MainLayout;
