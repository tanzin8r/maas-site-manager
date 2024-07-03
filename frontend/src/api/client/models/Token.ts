/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * A registration token for a site.
 */
export type Token = {
    id: number;
    value: string;
    audience: string;
    purpose: string;
    expired: string;
    created: string;
    site_id?: (number | null);
};

