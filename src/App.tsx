import "./App.scss";
import SitesList from "./components/SitesList";
import { QueryClient, QueryClientProvider } from "react-query";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <div className="row">
          <div className="col-12">
            <h1>MAAS Site Manager</h1>
            <SitesList />
          </div>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
