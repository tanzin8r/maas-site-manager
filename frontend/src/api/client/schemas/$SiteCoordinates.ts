/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $SiteCoordinates = {
    description: `Coordinates for a MAAS site.`,
    properties: {
        id: {
            type: 'number',
            isRequired: true,
        },
        coordinates: {
            type: 'any-of',
            contains: [{
                type: 'any[]',
                maxItems: 2,
                minItems: 2,
            }, {
                type: 'null',
            }],
        },
    },
} as const;
