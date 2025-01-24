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
                type: 'Coordinates',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
