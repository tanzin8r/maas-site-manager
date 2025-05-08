import { http, HttpResponse } from "msw";

import staticTileImage from "@/mocks/assets/static-tile.png";

export const tileHandler = http.get(/.*\.(?:png|jpg|jpeg|bmp)$/, async ({ request }) => {
  const url = new URL(request.url);
  if (url.host.includes("tile.openstreetmap.org")) {
    const image = await fetch(staticTileImage).then((res) => res.arrayBuffer());
    return new HttpResponse(image, {
      headers: {
        "Content-Type": "image/png",
      },
      status: 200,
    });
  }
});
