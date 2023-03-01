import { ContextualMenu, Icon, CheckboxInput } from "@canonical/react-components";

import "./ColumnsVisibilityControl.scss";
import type { SitesColumn } from "./SitesTable";

function ColumnsVisibilityControl({ columns }: { columns: SitesColumn[] }) {
  return (
    <ContextualMenu
      className="filter-accordion"
      constrainPanelWidth
      dropdownProps={{ "aria-label": "columns menu" }}
      position="left"
      toggleClassName="columns-visibility-toggle has-icon"
      toggleLabel={
        <>
          <Icon name="settings" /> Columns
        </>
      }
      toggleLabelFirst={true}
    >
      <div className="columns-visibility-select-wrapper u-no-padding--top">
        {columns
          .filter((column) => column.id !== "select")
          .map((column) => {
            return (
              <div className="columns-visibility-checkbox">
                <CheckboxInput
                  aria-label={column.id}
                  key={column.id}
                  label={column.id}
                  {...{
                    checked: column.getIsVisible(),
                    onChange: column.getToggleVisibilityHandler(),
                  }}
                />
              </div>
            );
          })}
      </div>
    </ContextualMenu>
  );
}

export default ColumnsVisibilityControl;
