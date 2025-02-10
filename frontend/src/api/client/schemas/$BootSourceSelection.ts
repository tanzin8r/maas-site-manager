/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $BootSourceSelection = {
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        boot_source_id: {
            type: 'number',
            isRequired: true,
        },
        label: {
            type: 'BootAssetLabel',
            isRequired: true,
        },
        os: {
            type: 'string',
            isRequired: true,
        },
        release: {
            type: 'string',
            isRequired: true,
        },
        arches: {
            type: 'array',
            contains: {
                type: 'string',
            },
            isRequired: true,
        },
    },
} as const;
