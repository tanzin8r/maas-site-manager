import type { FC } from "react";
import { useEffect } from "react";

import type { TileLayerOptions } from "leaflet";
import L from "leaflet";

import { useMapEvents } from "./hooks";
import type { MapProps } from "./types";

import LeafletMapContainer from "@/components/Map/LeafletMapContainer";
import MarkersLayer from "@/components/Map/MarkersLayer";
import { useLeafletMap } from "@/context/LeafletMapContext";
import useWindowSize from "@/hooks/useWindowSize";
import { computeMinZoom } from "@/utils";

const TileLayer = ({ url, attribution }: { url: string } & Pick<TileLayerOptions, "attribution">) => {
  const map = useLeafletMap();
  useEffect(() => {
    const tileLayer = L.tileLayer(url, { attribution }).addTo(map);
    return () => {
      map.removeLayer(tileLayer);
    };
  }, [map, url, attribution]);
  return null;
};

const Map: FC<MapProps> = ({ onBoundsChange, markers }) => {
  const map = useLeafletMap();

  const handleBoundsChange = useCallback(() => {
    onBoundsChange?.(map.getBounds().toBBoxString());
  }, [map, onBoundsChange]);

  useMapEvents({ zoomend: handleBoundsChange, moveend: handleBoundsChange });

  return (
    <>
      {markers ? <MarkersLayer markers={markers} /> : null}
      <TileLayer
        attribution={`<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>`}
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </>
  );
};

const MapContainer: FC<MapProps> = (props) => {
  const { screenHeight, screenWidth } = useWindowSize();
  const minZoom = useMemo(() => computeMinZoom({ screenHeight, screenWidth }), [screenHeight, screenWidth]);

  return (
    <LeafletMapContainer
      className="map"
      initialOptions={{
        center: [0, 0],
        zoom: 3,
        zoomControlOptions: { position: "bottomright" },
        maxBoundsViscosity: 0.8,
        maxZoom: 17,
        maxBounds: [
          [-90, -180],
          [90, 180],
        ],
        boundsOptions: { paddingTopLeft: [50, 0] },
      }}
      minZoom={minZoom}
    >
      <Map {...props} />
    </LeafletMapContainer>
  );
};

export default MapContainer;
