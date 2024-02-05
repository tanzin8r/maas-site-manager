/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TokensGetResponse = {
    description: `List of existing tokens.`,
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
                type: 'Token',
            },
            isRequired: true,
        },
    },
} as const;
