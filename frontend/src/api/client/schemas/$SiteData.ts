/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $SiteData = {
    description: `Data for a site.`,
    properties: {
        machines_total: {
            type: 'number',
            isRequired: true,
        },
        machines_allocated: {
            type: 'number',
            isRequired: true,
        },
        machines_deployed: {
            type: 'number',
            isRequired: true,
        },
        machines_ready: {
            type: 'number',
            isRequired: true,
        },
        machines_error: {
            type: 'number',
            isRequired: true,
        },
        machines_other: {
            type: 'number',
            isRequired: true,
        },
        last_seen: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
    },
} as const;
