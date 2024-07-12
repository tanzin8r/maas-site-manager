import { getGeoJson, renderToHtmlString } from "./utils";

import { markerFactory } from "@/mocks/factories";
import { act } from "@/utils/test-utils";

it("converts the React element to an HTML string", () => {
  act(() => {
    const Component = () => <div>Test</div>;
    expect(renderToHtmlString(<Component />)).toEqual("<div>Test</div>");
  });
});

it("converts SiteMarkers to GeoJSON", () => {
  const markers = markerFactory.buildList(2);

  const geojson = getGeoJson(markers);

  expect(geojson.features).toHaveLength(2);
});

it("omits markers that have no position", () => {
  const markers = [markerFactory.build({ position: undefined }), markerFactory.build()];

  const geojson = getGeoJson(markers);

  expect(geojson.features).toHaveLength(1);
});
