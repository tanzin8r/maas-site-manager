import { http, HttpResponse } from "msw";

import type { Token, TokensPostRequest, TokensPostResponse } from "@/api";
import { tokenFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const mockTokens = tokenFactory.buildList(155);
const tokensResolvers = {
  createTokens: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.tokens, async ({ request }) => {
        let tokens;
        const { count, duration } = (await request.json()) as TokensPostRequest;
        if (count && duration) {
          tokens = Array(count).fill(tokenFactory.build());
        } else {
          return new HttpResponse(null, { status: 400 });
        }
        const response: TokensPostResponse = { items: tokens };
        return HttpResponse.json(response);
      });
    },
  },
  listTokens: {
    resolved: false,
    handler: (data: Token[] = mockTokens) => {
      return http.get(apiUrls.tokens, ({ request }) => {
        const searchParams = new URL(request.url).searchParams;
        const page = Number(searchParams.get("page"));
        const size = Number(searchParams.get("size"));
        const itemsPage = data.slice((page - 1) * size, page * size);
        const response = {
          items: itemsPage,
          page,
          total: data.length,
        };
        tokensResolvers.listTokens.resolved = true;
        return HttpResponse.json(response);
      });
    },
  },
  deleteTokens: {
    resolved: false,
    handler: () => {
      return http.delete(apiUrls.tokens, () => {
        return new HttpResponse(null, { status: 204 });
      });
    },
  },
  exportTokens: {
    resolved: false,
    handler: () => {
      return http.get(apiUrls.tokensExport, () => {
        const csv = `id,value,expired,created
        9,0e846493-fde9-4d15-844c-2ca0341d1e84,2024-01-01 00:00:00,2023-02-28 00:00:00
        10,e15a7d3c-9df8-40c7-b81b-ed4796e777bc,2024-01-01 00:00:00,2023-02-28 00:00:00
        11,87a62d9a-7645-43b5-9dd4-eaf53e768c4a,2024-01-01 00:00:00,2023-02-28 00:00:00`;

        return new HttpResponse(csv, {
          status: 200,
          headers: {
            "Content-Type": "text/csv",
          },
        });
      });
    },
  },
};

export { tokensResolvers };
