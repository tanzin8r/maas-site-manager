/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $BootAssetsGetResponse = {
    properties: {
        total: {
            type: 'number',
            isRequired: true,
        },
        page: {
            type: 'number',
            isRequired: true,
        },
        size: {
            type: 'number',
            isRequired: true,
        },
        items: {
            type: 'array',
            contains: {
                type: 'BootAsset',
            },
            isRequired: true,
        },
    },
} as const;
