/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $UsersPostRequest = {
    description: `Request to create a User.`,
    properties: {
        full_name: {
            type: 'string',
            isRequired: true,
        },
        username: {
            type: 'string',
            isRequired: true,
        },
        email: {
            type: 'string',
            isRequired: true,
        },
        password: {
            type: 'string',
            isRequired: true,
            maxLength: 100,
            minLength: 8,
        },
        confirm_password: {
            type: 'string',
            isRequired: true,
            maxLength: 100,
            minLength: 8,
        },
        is_admin: {
            type: 'boolean',
        },
    },
} as const;
