/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TokensPostRequest = {
    description: `Request to create one or more tokens, with a certain validity.`,
    properties: {
        count: {
            type: 'number',
        },
        duration: {
            type: 'string',
            isRequired: true,
            format: 'duration',
        },
    },
} as const;
