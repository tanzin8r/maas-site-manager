/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Request to create a User.
 */
export type UsersPostRequest = {
    full_name: string;
    username: string;
    email: string;
    password: string;
    confirm_password: string;
    is_admin?: boolean;
};

