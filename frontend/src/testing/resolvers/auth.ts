import { http, HttpResponse } from "msw";

import { accessTokenFactory } from "@/mocks/factories";
import { apiUrls } from "@/utils/test-urls";

const authResolvers = {
  login: {
    resolved: false,
    handler: () => {
      return http.post(apiUrls.login, async () => {
        const accessToken = accessTokenFactory.build();
        authResolvers.login.resolved = true;
        return HttpResponse.json(accessToken);
      });
    },
  },
};

export { authResolvers };
