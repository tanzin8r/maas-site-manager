/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AccessTokenResponse } from '../models/AccessTokenResponse';
import type { Body_post_v1_login_post } from '../models/Body_post_v1_login_post';
import type { BootAssetsGetResponse } from '../models/BootAssetsGetResponse';
import type { BootSourceSelectionsGetResponse } from '../models/BootSourceSelectionsGetResponse';
import type { BootSourcesGetResponse } from '../models/BootSourcesGetResponse';
import type { PendingSitesGetResponse } from '../models/PendingSitesGetResponse';
import type { PendingSitesPostRequest } from '../models/PendingSitesPostRequest';
import type { Settings } from '../models/Settings';
import type { SettingsUpdate } from '../models/SettingsUpdate';
import type { Site } from '../models/Site';
import type { SiteCoordinates } from '../models/SiteCoordinates';
import type { SitesGetResponse } from '../models/SitesGetResponse';
import type { SiteUpdateRequest } from '../models/SiteUpdateRequest';
import type { TokensGetResponse } from '../models/TokensGetResponse';
import type { TokensPostRequest } from '../models/TokensPostRequest';
import type { TokensPostResponse } from '../models/TokensPostResponse';
import type { User } from '../models/User';
import type { UsersGetResponse } from '../models/UsersGetResponse';
import type { UsersPasswordPatchRequest } from '../models/UsersPasswordPatchRequest';
import type { UsersPatchMeRequest } from '../models/UsersPatchMeRequest';
import type { UsersPatchRequest } from '../models/UsersPatchRequest';
import type { UsersPostRequest } from '../models/UsersPostRequest';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class DefaultService {

    constructor(public readonly httpRequest: BaseHttpRequest) { }

    /**
     * Get Boot Assets
     * Return boot assets.
     * @returns BootAssetsGetResponse Successful Response
     * @throws ApiError
     */
    public getBootAssetsV1BootassetsGet({
        sortBy,
        page = 1,
        size = 20,
    }: {
        sortBy?: (string | null),
        page?: number,
        size?: number,
    }): CancelablePromise<BootAssetsGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/bootassets',
            query: {
                'sort_by': sortBy,
                'page': page,
                'size': size,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Boot Sources
     * Return boot sources.
     * @returns BootSourcesGetResponse Successful Response
     * @throws ApiError
     */
    public getBootSourcesV1BootassetSourcesGet({
        sortBy,
        page = 1,
        size = 20,
    }: {
        sortBy?: (string | null),
        page?: number,
        size?: number,
    }): CancelablePromise<BootSourcesGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/bootasset-sources',
            query: {
                'sort_by': sortBy,
                'page': page,
                'size': size,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Boot Source Selections
     * Return boot source selections.
     * @returns BootSourceSelectionsGetResponse Successful Response
     * @throws ApiError
     */
    public getBootSourceSelectionsV1BootassetSourcesIdSelectionsGet({
        id,
        sortBy,
        page = 1,
        size = 20,
    }: {
        id: number,
        sortBy?: (string | null),
        page?: number,
        size?: number,
    }): CancelablePromise<BootSourceSelectionsGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/bootasset-sources/{id}/selections',
            path: {
                'id': id,
            },
            query: {
                'sort_by': sortBy,
                'page': page,
                'size': size,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Post
     * @returns AccessTokenResponse Successful Response
     * @throws ApiError
     */
    public postV1LoginPost({
        formData,
    }: {
        formData: Body_post_v1_login_post,
    }): CancelablePromise<AccessTokenResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/login',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get
     * Return service settings.
     * @returns Settings Successful Response
     * @throws ApiError
     */
    public getV1SettingsGet(): CancelablePromise<Settings> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/settings',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
            },
        });
    }

    /**
     * Patch
     * @returns any Successful Response
     * @throws ApiError
     */
    public patchV1SettingsPatch({
        requestBody,
    }: {
        requestBody: SettingsUpdate,
    }): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/v1/settings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Pending
     * Return pending sites.
     * @returns PendingSitesGetResponse Successful Response
     * @throws ApiError
     */
    public getPendingV1SitesPendingGet({
        page = 1,
        size = 20,
    }: {
        page?: number,
        size?: number,
    }): CancelablePromise<PendingSitesGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/sites/pending',
            query: {
                'page': page,
                'size': size,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Post Pending
     * Accept or reject pending sites.
     * @returns void
     * @throws ApiError
     */
    public postPendingV1SitesPendingPost({
        requestBody,
    }: {
        requestBody: PendingSitesPostRequest,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/sites/pending',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get
     * Return accepted sites.
     * @returns SitesGetResponse Successful Response
     * @throws ApiError
     */
    public getV1SitesGet({
        coordinates,
        page = 1,
        size = 20,
        city,
        country,
        name,
        note,
        state,
        address,
        postalCode,
        timezone,
        url,
        clusterUuid,
        q,
        sortBy,
    }: {
        coordinates?: (boolean | null),
        page?: number,
        size?: number,
        city?: (Array<string> | null),
        country?: (Array<string> | null),
        name?: (Array<string> | null),
        note?: (Array<string> | null),
        state?: (Array<string> | null),
        address?: (Array<string> | null),
        postalCode?: (Array<string> | null),
        timezone?: (Array<string> | null),
        url?: (Array<string> | null),
        clusterUuid?: (Array<string> | null),
        q?: (string | null),
        sortBy?: (string | null),
    }): CancelablePromise<SitesGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/sites',
            query: {
                'coordinates': coordinates,
                'page': page,
                'size': size,
                'city': city,
                'country': country,
                'name': name,
                'note': note,
                'state': state,
                'address': address,
                'postal_code': postalCode,
                'timezone': timezone,
                'url': url,
                'cluster_uuid': clusterUuid,
                'q': q,
                'sort_by': sortBy,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Delete Many
     * Delete multiple sites from the database.
     * @returns void
     * @throws ApiError
     */
    public deleteManyV1SitesDelete({
        ids,
    }: {
        ids: Array<number>,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/v1/sites',
            query: {
                'ids': ids,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Coordinates
     * Return coordinates for all accepted sites.
     * @returns SiteCoordinates Successful Response
     * @throws ApiError
     */
    public getCoordinatesV1SitesCoordinatesGet({
        city,
        country,
        name,
        note,
        state,
        address,
        postalCode,
        timezone,
        url,
        clusterUuid,
        q,
    }: {
        city?: (Array<string> | null),
        country?: (Array<string> | null),
        name?: (Array<string> | null),
        note?: (Array<string> | null),
        state?: (Array<string> | null),
        address?: (Array<string> | null),
        postalCode?: (Array<string> | null),
        timezone?: (Array<string> | null),
        url?: (Array<string> | null),
        clusterUuid?: (Array<string> | null),
        q?: (string | null),
    }): CancelablePromise<Array<SiteCoordinates>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/sites/coordinates',
            query: {
                'city': city,
                'country': country,
                'name': name,
                'note': note,
                'state': state,
                'address': address,
                'postal_code': postalCode,
                'timezone': timezone,
                'url': url,
                'cluster_uuid': clusterUuid,
                'q': q,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Id
     * Return a specific site.
     * @returns Site Successful Response
     * @throws ApiError
     */
    public getIdV1SitesIdGet({
        id,
    }: {
        id: number,
    }): CancelablePromise<Site> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/sites/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Patch
     * Modify a site.
     * @returns Site Successful Response
     * @throws ApiError
     */
    public patchV1SitesIdPatch({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: SiteUpdateRequest,
    }): CancelablePromise<Site> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/v1/sites/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                404: `Not Found`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Delete
     * Delete a site from the database.
     * @returns void
     * @throws ApiError
     */
    public deleteV1SitesIdDelete({
        id,
    }: {
        id: number,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/v1/sites/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get
     * Return all tokens.
     * @returns TokensGetResponse Successful Response
     * @throws ApiError
     */
    public getV1TokensGet({
        page = 1,
        size = 20,
        id,
        value,
        siteId,
    }: {
        page?: number,
        size?: number,
        id?: (Array<number> | null),
        value?: (Array<string> | null),
        siteId?: (Array<number> | null),
    }): CancelablePromise<TokensGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/tokens',
            query: {
                'page': page,
                'size': size,
                'id': id,
                'value': value,
                'site_id': siteId,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Post
     * Create enrollment tokens for sites.
     *
     * Token duration (TTL) is expressed as an ISO-8601 duration string.
     * @returns TokensPostResponse Successful Response
     * @throws ApiError
     */
    public postV1TokensPost({
        requestBody,
    }: {
        requestBody: TokensPostRequest,
    }): CancelablePromise<TokensPostResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/tokens',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Delete Many
     * Delete several tokens from the database
     * @returns void
     * @throws ApiError
     */
    public deleteManyV1TokensDelete({
        ids,
    }: {
        ids: Array<number>,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/v1/tokens',
            query: {
                'ids': ids,
            },
            errors: {
                401: `Unauthorized`,
                404: `Not Found`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Export
     * Return the list of active tokens in CSV format.
     * @returns any Successful Response
     * @throws ApiError
     */
    public getExportV1TokensExportGet({
        page = 1,
        size = 20,
        id,
        value,
        siteId,
    }: {
        page?: number,
        size?: number,
        id?: (Array<number> | null),
        value?: (Array<string> | null),
        siteId?: (Array<number> | null),
    }): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/tokens/export',
            query: {
                'page': page,
                'size': size,
                'id': id,
                'value': value,
                'site_id': siteId,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Delete
     * Delete a token from the database.
     * @returns void
     * @throws ApiError
     */
    public deleteV1TokensIdDelete({
        id,
    }: {
        id: number,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/v1/tokens/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get
     * Return all users
     * @returns UsersGetResponse Successful Response
     * @throws ApiError
     */
    public getV1UsersGet({
        page = 1,
        size = 20,
        email,
        username,
        fullName,
        isAdmin,
        sortBy,
        searchText = '',
    }: {
        page?: number,
        size?: number,
        email?: (Array<string> | null),
        username?: (Array<string> | null),
        fullName?: (Array<string> | null),
        isAdmin?: (Array<boolean> | null),
        sortBy?: (string | null),
        searchText?: string,
    }): CancelablePromise<UsersGetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/users',
            query: {
                'page': page,
                'size': size,
                'email': email,
                'username': username,
                'full_name': fullName,
                'is_admin': isAdmin,
                'sort_by': sortBy,
                'search_text': searchText,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Post
     * Create a user.
     * @returns User Successful Response
     * @throws ApiError
     */
    public postV1UsersPost({
        requestBody,
    }: {
        requestBody: UsersPostRequest,
    }): CancelablePromise<User> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/v1/users',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Me
     * Render info about the authenticated user.
     * @returns User Successful Response
     * @throws ApiError
     */
    public getMeV1UsersMeGet(): CancelablePromise<User> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/users/me',
            errors: {
                401: `Unauthorized`,
            },
        });
    }

    /**
     * Patch Me
     * Update the details for a user
     * @returns User Successful Response
     * @throws ApiError
     */
    public patchMeV1UsersMePatch({
        requestBody,
    }: {
        requestBody: UsersPatchMeRequest,
    }): CancelablePromise<User> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/v1/users/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Patch Me Password
     * Modify the users password.
     * @returns any Successful Response
     * @throws ApiError
     */
    public patchMePasswordV1UsersMePasswordPatch({
        requestBody,
    }: {
        requestBody: UsersPasswordPatchRequest,
    }): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/v1/users/me/password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Get Id
     * Select a specific user
     * @returns User Successful Response
     * @throws ApiError
     */
    public getIdV1UsersIdGet({
        id,
    }: {
        id: number,
    }): CancelablePromise<User> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/v1/users/{id}',
            path: {
                'id': id,
            },
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Patch
     * Admin action to update the details for a user.
     * @returns User Successful Response
     * @throws ApiError
     */
    public patchV1UsersIdPatch({
        id,
        requestBody,
    }: {
        id: number,
        requestBody: UsersPatchRequest,
    }): CancelablePromise<User> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/v1/users/{id}',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Not Found`,
                422: `Unprocessable Entity`,
            },
        });
    }

    /**
     * Delete
     * Delete a user from the database.
     * @returns void
     * @throws ApiError
     */
    public deleteV1UsersIdDelete({
        id,
    }: {
        id: number,
    }): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/v1/users/{id}',
            path: {
                'id': id,
            },
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                403: `Forbidden`,
                422: `Unprocessable Entity`,
            },
        });
    }

}
