import { Button, Col, Row } from "@canonical/react-components";
import { Link } from "react-router-dom";

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
          <div className="u-flex u-flex--justify-end">
            <Button>Export</Button>
            <Button appearance="negative">Delete</Button>
            <Link className="p-button--positive" role="button" state={{ sidebar: true }} to="">
              Generate tokens
            </Link>
          </div>
        </Col>
      </Row>
    </section>
  );
};

export default TokensList;
