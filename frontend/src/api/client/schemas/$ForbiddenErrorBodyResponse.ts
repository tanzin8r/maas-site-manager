/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $ForbiddenErrorBodyResponse = {
    properties: {
        code: {
            type: 'all-of',
            contains: [{
                type: 'ExceptionCode',
            }],
        },
        message: {
            type: 'string',
        },
        details: {
            type: 'any-of',
            contains: [{
                type: 'array',
                contains: {
                    type: 'BaseExceptionDetail',
                },
            }, {
                type: 'null',
            }],
        },
        status_code: {
            type: 'number',
        },
    },
} as const;
