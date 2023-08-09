import { ContextualMenu, Icon, CheckboxInput } from "@canonical/react-components";

import type { SitesColumn } from "@/components/SitesList/SitesTable/SitesTable";

function ColumnsVisibilityControl({ columns }: { columns: SitesColumn[] }) {
  const filteredColumns = columns.filter(
    (column) => column.id !== "select" && column.id !== "name" && column.id !== "actions",
  );
  const hiddenColumns = filteredColumns.filter((column) => column.getIsVisible() === false);
  const selectedColumnsLength = filteredColumns.length - hiddenColumns.length;
  const someColumnsChecked = selectedColumnsLength > 0 && selectedColumnsLength < filteredColumns.length;

  const handleToggleAll = (isChecked: boolean) => {
    filteredColumns
      // If the "select all" checkbox is checked, find all hidden columns. Otherwise, find all visible columns
      .filter((column) => (isChecked ? column.getIsVisible() === false : column.getIsVisible() === true))
      .forEach((column) => column.toggleVisibility());
  };

  return (
    <ContextualMenu
      dropdownProps={{ "aria-label": "columns menu" }}
      position="right"
      toggleAppearance="base"
      toggleClassName="columns-visibility-control is-dense"
      toggleLabel={<Icon name="settings">Columns</Icon>}
      toggleLabelFirst={true}
    >
      <div className="columns-visibility-select-wrapper u-no-padding--top">
        <div className="columns-visibility-checkbox">
          <CheckboxInput
            checked={hiddenColumns.length === 0}
            indeterminate={someColumnsChecked}
            label={`${selectedColumnsLength} out of ${filteredColumns.length} selected`}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              handleToggleAll(e.target.checked);
            }}
          />
        </div>
      </div>
      <hr />
      <div className="columns-visibility-select-wrapper u-no-padding--top">
        {filteredColumns.map((column) => {
          return (
            <div className="columns-visibility-checkbox u-capitalize" key={column.id}>
              <CheckboxInput
                aria-label={column.id}
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
