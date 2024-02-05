/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $PendingSitesPostRequest = {
    description: `Request to accept/reject sites.`,
    properties: {
        ids: {
            type: 'array',
            contains: {
                type: 'number',
            },
            isRequired: true,
        },
        accept: {
            type: 'boolean',
            isRequired: true,
        },
    },
} as const;
