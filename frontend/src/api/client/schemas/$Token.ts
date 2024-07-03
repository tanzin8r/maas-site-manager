/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Token = {
    description: `A registration token for a site.`,
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        value: {
            type: 'string',
            isRequired: true,
        },
        audience: {
            type: 'string',
            isRequired: true,
        },
        purpose: {
            type: 'string',
            isRequired: true,
        },
        expired: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        created: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        site_id: {
            type: 'any-of',
            contains: [{
                type: 'number',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
