import { Button, Icon, Tooltip } from "@canonical/react-components";
import classNames from "classnames";

import type { BootSourceColumnDef } from "./types";
import { BootSourceStatus } from "./types";

import { useAppLayoutContext } from "@/context";
import { useBootSourceContext } from "@/context/BootSourceContext";
import { createAccessor } from "@/utils";

export const useImageSourceTableColumns = () => {
  const { setSidebar } = useAppLayoutContext();
  const { setSelected } = useBootSourceContext();

  return useMemo<BootSourceColumnDef[]>(
    () => [
      {
        id: "url",
        enableSorting: false,
        header: () => <div>Source</div>,
        accessorFn: createAccessor("url"),
        accessorKey: "url",
        cell: ({ getValue }) => {
          const { url } = getValue();
          return (
            <div>
              {url === "custom" ? (
                <>
                  Custom images{" "}
                  <Tooltip
                    message="This row represents the custom images that can be uploaded to MAAS Site Manager. You can edit its priority in this screen."
                    position="right"
                  >
                    <Icon name="help" />
                  </Tooltip>
                </>
              ) : (
                url
              )}
            </div>
          );
        },
      },
      {
        id: "status",
        enableSorting: false,
        header: () => <div className="status-text">Status</div>,
        accessorFn: createAccessor(["status", "url"]),
        accessorKey: "status",
        cell: ({ getValue }) => {
          const { status, url } = getValue();
          if (url !== "custom") {
            return (
              <div
                className={classNames("status-icon", {
                  "is-lost": BootSourceStatus[status] !== BootSourceStatus.connected,
                  "is-stable": BootSourceStatus[status] === BootSourceStatus.connected,
                })}
              >
                {BootSourceStatus[status]}
              </div>
            );
          } else {
            return <div />;
          }
        },
      },
      {
        id: "syncing",
        enableSorting: false,
        header: () => <div>Syncing</div>,
        accessorFn: createAccessor(["sync_interval", "url"]),
        accessorKey: "syncing",
        cell: ({ getValue }) => {
          const { sync_interval, url } = getValue();
          if (url === "custom") {
            return <div />;
          }

          return (
            <div>
              {sync_interval > 0 ? (
                <Icon aria-label="Source is syncing" name="task-outstanding" />
              ) : (
                <Icon aria-label="Source is not syncing" name="error-grey" />
              )}
            </div>
          );
        },
      },
      {
        id: "total_images",
        enableSorting: false,
        header: () => <div>Number of images</div>,
        accessorFn: createAccessor("total_images"),
        accessorKey: "total_images",
        cell: ({ getValue }) => {
          const { total_images } = getValue();
          return <div>{total_images}</div>;
        },
      },
      {
        id: "keyring",
        enableSorting: false,
        header: () => <div>Signed with GPG key</div>,
        accessorFn: createAccessor(["keyring", "status", "url"]),
        accessorKey: "keyring",
        cell: ({ getValue }) => {
          const { keyring, status, url } = getValue();
          if (url === "custom") {
            return <div />;
          } else if (!keyring || status === "gpg_error") {
            return <Icon aria-label="Not signed with GPG key" name="error-grey" />;
          } else {
            return <Icon aria-label="Signed with GPG key" name="task-outstanding" />;
          }
        },
      },
      {
        id: "priority",
        enableSorting: false,
        header: () => (
          <div>
            Priority{" "}
            <Tooltip
              message="If the same image is available from several sources, the image from the source with the higher priority takes precedence. 1 is the highest priority."
              position="btm-center"
            >
              <Icon name="help" />
            </Tooltip>
          </div>
        ),
        accessorFn: createAccessor("priority"),
        accessorKey: "priority",
        cell: ({ getValue }) => {
          const { priority } = getValue();
          return <div>{priority}</div>;
        },
      },
      {
        id: "actions",
        enableSorting: false,
        header: () => <div>Actions</div>,
        accessorFn: createAccessor(["url", "id"]),
        accessorKey: "url",
        cell: ({ getValue }) => {
          const { url, id } = getValue();
          return (
            <div>
              <Button
                appearance="base"
                aria-label="Edit image source"
                className="is-dense u-table-cell-padding-overlap"
                // TODO: enable this once side panel is available https://warthogs.atlassian.net/browse/MAASENG-4381
                onClick={() => {
                  setSelected(id);
                  setSidebar(null);
                }}
              >
                <Icon name="edit" />
              </Button>
              {url !== "custom" && (
                <Button
                  appearance="base"
                  aria-label="Delete image source"
                  className="is-dense u-table-cell-padding-overlap"
                  onClick={() => {
                    setSelected(id);
                    setSidebar("deleteBootSource");
                  }}
                >
                  <Icon name="delete" />
                </Button>
              )}
            </div>
          );
        },
      },
    ],
    [setSidebar, setSelected],
  );
};
