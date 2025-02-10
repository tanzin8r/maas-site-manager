/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BootAssetLabel } from './BootAssetLabel';

export type BootSourceSelection = {
    id: number;
    boot_source_id: number;
    label: BootAssetLabel;
    os: string;
    release: string;
    arches: Array<string>;
};

