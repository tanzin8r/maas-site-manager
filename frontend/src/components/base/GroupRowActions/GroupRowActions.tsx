import { Button, Icon } from "@canonical/react-components";

const GroupRowActions = ({
  toggleExpanded,
  getIsExpanded,
}: {
  toggleExpanded: () => void;
  getIsExpanded: () => boolean;
}) => (
  <Button
    appearance="base"
    dense
    hasIcon
    onClick={() => {
      toggleExpanded();
    }}
    type="button"
  >
    {getIsExpanded() ? <Icon name="minus">Collapse</Icon> : <Icon name="plus">Expand</Icon>}
  </Button>
);

export default GroupRowActions;
