/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $AccessTokenResponse = {
    description: `Content for a response returning a JWT.`,
    properties: {
        token_type: {
            type: 'string',
            isRequired: true,
        },
        access_token: {
            type: 'string',
            isRequired: true,
        },
    },
} as const;
