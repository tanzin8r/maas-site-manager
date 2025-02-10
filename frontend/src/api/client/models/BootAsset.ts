/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BootAssetKind } from './BootAssetKind';
import type { BootAssetLabel } from './BootAssetLabel';

export type BootAsset = {
    id: number;
    boot_source_id: number;
    kind: BootAssetKind;
    label: BootAssetLabel;
    os: string;
    release: string;
    codename: string;
    title: string;
    arch: string;
    subarch: string;
    compatibility: Array<string>;
    flavor: string;
    base_image: string;
    eol: string;
    esm_eol: string;
};

