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
        },
        country: {
            type: 'string',
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
        },
        state: {
            type: 'string',
        },
        address: {
            type: 'string',
        },
        postal_code: {
            type: 'string',
        },
        timezone: {
            type: 'any-of',
            contains: [{
                type: 'TimeZone',
            }, {
                type: 'Enum',
            }],
        },
        url: {
            type: 'string',
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
        },
    },
} as const;
