/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $SitesGetResponse = {
    description: `Response with paginated accepted sites.`,
    properties: {
        total: {
            type: 'number',
            isRequired: true,
        },
        page: {
            type: 'number',
            isRequired: true,
        },
        size: {
            type: 'number',
            isRequired: true,
        },
        items: {
            type: 'array',
            contains: {
                type: 'Site',
            },
            isRequired: true,
        },
    },
} as const;
