/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Settings = {
    description: `Application settings that can be changed via the API.`,
    properties: {
        service_url: {
            type: 'string',
        },
        enrolment_url: {
            type: 'string',
        },
        token_lifetime_minutes: {
            type: 'number',
        },
        token_rotation_interval_minutes: {
            type: 'number',
        },
    },
} as const;
