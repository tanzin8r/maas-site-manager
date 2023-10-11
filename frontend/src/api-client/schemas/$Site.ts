/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Site = {
    description: `A MAAS installation.`,
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        name: {
            type: 'string',
            isRequired: true,
        },
        city: {
            type: 'string',
            isRequired: true,
        },
        country: {
            type: 'string',
            isRequired: true,
        },
        coordinates: {
            type: 'any-of',
            contains: [{
                type: 'any[]',
                maxItems: 2,
                minItems: 2,
            }, {
                type: 'null',
            }],
            isRequired: true,
        },
        note: {
            type: 'string',
            isRequired: true,
        },
        state: {
            type: 'string',
            isRequired: true,
        },
        address: {
            type: 'string',
            isRequired: true,
        },
        postal_code: {
            type: 'string',
            isRequired: true,
        },
        timezone: {
            type: 'any-of',
            contains: [{
                type: 'TimeZone',
            }],
            isRequired: true,
        },
        url: {
            type: 'string',
            isRequired: true,
        },
        name_unique: {
            type: 'boolean',
            isRequired: true,
        },
        connection_status: {
            type: 'ConnectionStatus',
            isRequired: true,
        },
        stats: {
            type: 'any-of',
            contains: [{
                type: 'SiteData',
            }, {
                type: 'null',
            }],
            isRequired: true,
        },
    },
} as const;
