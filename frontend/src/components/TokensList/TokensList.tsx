import { Button, Col, Row } from "@canonical/react-components";
import { Outlet, Link } from "react-router-dom";

const TokensList = () => {
  return (
    <section>
      <Row>
        <Col size={2}>
          <h2 className="p-heading--4">Tokens</h2>
        </Col>
      </Row>
      <Row>
        <Col size={12}>
          <Button>Export</Button>
          <Button appearance="negative">Delete</Button>
          <Link to="create">
            <Button appearance="positive" element="a">
              Generate tokens
            </Button>
          </Link>
        </Col>
      </Row>
      <Outlet />
    </section>
  );
};

export default TokensList;
