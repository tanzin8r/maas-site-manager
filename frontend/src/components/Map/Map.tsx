import type { MapContainerProps } from "react-leaflet";
import { MapContainer, TileLayer } from "react-leaflet";

const Map = ({ id = "map-container" }: MapContainerProps) => {
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
    >
      <TileLayer data-testid="tile-layer" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    </MapContainer>
  );
};

export default Map;
