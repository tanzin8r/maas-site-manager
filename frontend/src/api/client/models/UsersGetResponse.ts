/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { User } from './User';

/**
 * List of existing users.
 */
export type UsersGetResponse = {
    total: number;
    page: number;
    size: number;
    items: Array<User>;
};

