import { useId } from "react";

import { Form, Input, Button } from "@canonical/react-components";

const TokensCreate = () => {
  const id = useId();
  return (
    <div>
      <Form aria-labelledby={id}>
        <h3 id={id}>Generate new enrollment tokens</h3>
        <Input label="Amount of tokens to generate" type="number" />
        <Input label="Expiration time" type="text" />
        <p className="u-text--muted">
          Use this token once to request an enrolment in the specified timeframe. <br />
          Allowed time units are seconds, minutes, hours, days and weeks.
        </p>
        <Button type="button">Cancel</Button>
        <Button appearance="positive" type="submit">
          Generate token
        </Button>
      </Form>
    </div>
  );
};

export default TokensCreate;
