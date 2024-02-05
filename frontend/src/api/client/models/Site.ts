/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { ConnectionStatus } from './ConnectionStatus';
import type { SiteData } from './SiteData';
import type { TimeZone } from './TimeZone';

/**
 * A MAAS installation.
 */
export type Site = {
    id: number;
    name: string;
    city?: string;
    country?: string;
    coordinates: (any[] | null);
    note?: string;
    state?: string;
    address?: string;
    postal_code?: string;
    timezone?: TimeZone;
    url?: string;
    name_unique: boolean;
    connection_status: ConnectionStatus;
    stats?: (SiteData | null);
};

