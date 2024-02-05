/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $UsersPasswordPatchRequest = {
    description: `User password change schema.`,
    properties: {
        current_password: {
            type: 'string',
            isRequired: true,
        },
        new_password: {
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
    },
} as const;
