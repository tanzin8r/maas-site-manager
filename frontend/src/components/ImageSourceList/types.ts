import type { ColumnDef } from "@tanstack/react-table";

export type BootSourceColumnDef = ColumnDef<BootSource, BootSource>;

// temporary type until API is ready
export type BootSource = {
  id: number;
  url: string | "custom";
  keyring: string;
  sync_interval: number;
  priority: number;
  status: keyof typeof BootSourceStatus;
  total_images: number;
};

export const BootSourceStatus = {
  connected: "Connected",
  unreachable: "Server unreachable",
  gpg_error: "GPG Signature invalid",
} as const;
