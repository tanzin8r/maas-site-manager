/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { TimeZone } from './TimeZone';

/**
 * Update a site.
 */
export type SiteUpdateRequest = {
    city?: (string | null);
    country?: (string | null);
    coordinates?: (Array<number> | null);
    note?: (string | null);
    state?: (string | null);
    address?: (string | null);
    postal_code?: (string | null);
    timezone?: (TimeZone | null);
};

