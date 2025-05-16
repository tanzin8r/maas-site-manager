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
    handler: (data: Token[] = mockTokens) => {
      return http.get(apiUrls.tokensExport, ({ request }) => {
        const url = new URL(request.url);
        const idsParam = url.searchParams.getAll("id");

        let filteredTokens = data;
        if (idsParam.length > 0) {
          const requestedIds = idsParam.map((id) => parseInt(id.trim(), 10));
          filteredTokens = data.filter((token) => requestedIds.includes(token.id));
        }

        const csv = [
          "id,value,expired,created",
          ...filteredTokens.map((t) => `${t.id},${t.value},${t.expired},${t.created}`),
        ].join("\n");

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
