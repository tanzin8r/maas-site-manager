/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $BootSource = {
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        priority: {
            type: 'number',
            isRequired: true,
        },
        url: {
            type: 'string',
            isRequired: true,
        },
        keyring: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        sync_interval: {
            type: 'number',
            isRequired: true,
        },
    },
} as const;
