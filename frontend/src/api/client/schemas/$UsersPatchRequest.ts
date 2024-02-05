/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $UsersPatchRequest = {
    description: `Request to edit details for a User.`,
    properties: {
        full_name: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        username: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        email: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        password: {
            type: 'any-of',
            contains: [{
                type: 'string',
                maxLength: 100,
                minLength: 8,
            }, {
                type: 'null',
            }],
        },
        confirm_password: {
            type: 'any-of',
            contains: [{
                type: 'string',
                maxLength: 100,
                minLength: 8,
            }, {
                type: 'null',
            }],
        },
        is_admin: {
            type: 'any-of',
            contains: [{
                type: 'boolean',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
