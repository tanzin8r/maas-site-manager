/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $BootAsset = {
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        boot_source_id: {
            type: 'number',
            isRequired: true,
        },
        kind: {
            type: 'BootAssetKind',
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
        codename: {
            type: 'string',
            isRequired: true,
        },
        title: {
            type: 'string',
            isRequired: true,
        },
        arch: {
            type: 'string',
            isRequired: true,
        },
        subarch: {
            type: 'string',
            isRequired: true,
        },
        compatibility: {
            type: 'array',
            contains: {
                type: 'string',
            },
            isRequired: true,
        },
        flavor: {
            type: 'string',
            isRequired: true,
        },
        base_image: {
            type: 'string',
            isRequired: true,
        },
        eol: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
        esm_eol: {
            type: 'string',
            isRequired: true,
            format: 'date-time',
        },
    },
} as const;
