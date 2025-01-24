/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BaseExceptionDetail } from './BaseExceptionDetail';
import type { ExceptionCode } from './ExceptionCode';

export type BadRequestErrorBodyResponse = {
    code?: ExceptionCode;
    message?: string;
    details?: (Array<BaseExceptionDetail> | null);
    status_code?: number;
};

