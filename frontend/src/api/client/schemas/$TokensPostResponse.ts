/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TokensPostResponse = {
    description: `Response containing generated tokens.`,
    properties: {
        items: {
            type: 'array',
            contains: {
                type: 'Token',
            },
            isRequired: true,
        },
    },
} as const;
