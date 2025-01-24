/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $BaseExceptionDetail = {
    description: `Additional details for an exception.`,
    properties: {
        reason: {
            type: 'string',
            isRequired: true,
        },
        messages: {
            type: 'array',
            contains: {
                type: 'string',
            },
            isRequired: true,
        },
        field: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
        location: {
            type: 'any-of',
            contains: [{
                type: 'string',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
