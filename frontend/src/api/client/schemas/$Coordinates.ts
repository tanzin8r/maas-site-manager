/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $Coordinates = {
    properties: {
        latitude: {
            type: 'number',
            maximum: 90,
            minimum: -90,
        },
        longitude: {
            type: 'number',
            maximum: 180,
            minimum: -180,
        },
    },
} as const;
