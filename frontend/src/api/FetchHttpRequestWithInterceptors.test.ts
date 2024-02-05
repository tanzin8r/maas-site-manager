import { rest } from "msw";
import { setupServer } from "msw/node";

import type { ResponseInterceptor } from "./FetchHttpRequestWithInterceptors";
import { FetchHttpRequestWithInterceptors } from "./FetchHttpRequestWithInterceptors";
import { baseURL } from "./config";

import { ApiError, OpenAPI } from "@/api/client";
import type { ApiRequestOptions } from "@/api/client/core/ApiRequestOptions";
import { apiUrls } from "@/utils/test-urls";
const server = setupServer();

let fetchHttpRequestWithInterceptors: FetchHttpRequestWithInterceptors;
let mockInterceptor: ResponseInterceptor;
const url = apiUrls.sites;
const relativeUrl = apiUrls.sites.replace(baseURL, "");

beforeAll(() => {
  server.listen();
});

afterAll(() => {
  server.close();
});

beforeEach(() => {
  mockInterceptor = vi.fn();
  fetchHttpRequestWithInterceptors = new FetchHttpRequestWithInterceptors({ ...OpenAPI, BASE: baseURL });
  fetchHttpRequestWithInterceptors.addResponseInterceptor(mockInterceptor);
});

it("should call interceptor for a successful response", async () => {
  const responseData = { success: true };
  server.use(
    rest.get(url, (req, res, ctx) => {
      return res(ctx.json(responseData));
    }),
  );
  const requestOptions = { url: relativeUrl, method: "GET" } as ApiRequestOptions;
  const responsePromise = fetchHttpRequestWithInterceptors.request(requestOptions);

  await expect(responsePromise).resolves.toEqual(responseData);
  expect(mockInterceptor).toHaveBeenCalledWith(responseData, null);
});

it("should call interceptor for a failed response", async () => {
  server.use(
    rest.get(url, (req, res, ctx) => {
      return res(ctx.status(500), ctx.text("Something went wrong"));
    }),
  );
  const requestOptions = { url: relativeUrl, method: "GET" } as ApiRequestOptions;

  await expect(fetchHttpRequestWithInterceptors.request(requestOptions)).rejects.toThrowError(expect.any(Error));
  expect(mockInterceptor).toHaveBeenCalledWith(null, expect.any(ApiError));
});
