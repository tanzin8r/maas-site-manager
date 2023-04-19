import { Col, Row, Strip } from "@canonical/react-components";
import { useLocation } from "react-router-dom";

const NotFound = () => {
  const location = useLocation();
  return (
    <Strip>
      <Row>
        <Col emptyLarge={4} size={6}>
          <h2>404: Page not found</h2>
          <p>Can't find page for: {location.pathname}</p>
        </Col>
      </Row>
    </Strip>
  );
};

export default NotFound;
