import type { MapContainerProps } from "react-leaflet";
import { MapContainer, TileLayer, ZoomControl } from "react-leaflet";

import SiteMarker from "./SiteMarker";
import { type SiteMarkerType } from "./types";

const Map = ({ id = "map-container", markers }: MapContainerProps & { markers: SiteMarkerType[] | null }) => {
  return (
    <MapContainer
      boundsOptions={{
        // TODO: set the correct padding to accomodate for SitesTableControls and the sidebar
        paddingTopLeft: [50, 0],
      }}
      center={[0, 0]}
      className="map"
      id={id}
      zoom={3}
      zoomControl={false}
    >
      <ZoomControl position="bottomright" />
      <TileLayer
        attribution='<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'
        data-testid="tile-layer"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers?.map(({ position, id, name }) => <SiteMarker id={id} key={id} name={name} position={position} />)}
    </MapContainer>
  );
};

export default Map;
