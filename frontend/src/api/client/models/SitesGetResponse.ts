/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Site } from './Site';

/**
 * Response with paginated accepted sites.
 */
export type SitesGetResponse = {
    total: number;
    page: number;
    size: number;
    items: Array<Site>;
};

