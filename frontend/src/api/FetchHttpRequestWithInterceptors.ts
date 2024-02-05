import { BaseHttpRequest, CancelablePromise } from "@/api/client";
import type { ApiError } from "@/api/client";
import type { ApiRequestOptions } from "@/api/client/core/ApiRequestOptions";
import { request } from "@/api/client/core/request";

export type ResponseInterceptor = (response: unknown, error: ApiError | null) => unknown;

export class FetchHttpRequestWithInterceptors extends BaseHttpRequest {
  protected responseInterceptors: ResponseInterceptor[] = [];

  public addResponseInterceptor(interceptor: ResponseInterceptor) {
    this.responseInterceptors.push(interceptor);
  }

  protected async handleResponse<T>(responsePromise: CancelablePromise<T>): Promise<T> {
    return new CancelablePromise(async (resolve, reject) => {
      try {
        const response = await responsePromise;
        if (this.responseInterceptors.length) {
          for (const interceptor of this.responseInterceptors) {
            interceptor(response, null);
          }
        }
        return resolve(response);
      } catch (error) {
        if (this.responseInterceptors.length) {
          for (const interceptor of this.responseInterceptors) {
            interceptor(null, error as ApiError);
          }
        }
        return reject(error);
      }
    });
  }

  public override request<T>(options: ApiRequestOptions): CancelablePromise<T> {
    const responsePromise = request<T>(this.config, options);
    return this.handleResponse<T>(responsePromise) as CancelablePromise<T>;
  }
}
