import { Spinner } from "@canonical/react-components";
import useLocalStorageState from "use-local-storage-state";

import MarkersLayer from "./MarkersLayer";
import { naturalEarth, osm } from "./styleSpecs";
import type { MapProps } from "./types";
import { getGeoJson } from "./utils";

import { useCurrentUser } from "@/app/api/query/users";
import type { MapSettingsStorageState } from "@/app/settings/views/MapSettings/MapSettings";
import MapContainer from "@/app/sites/views/SitesMap/components/Map/MapContainer";

const Map: React.FC<MapProps> = ({ markers }) => {
  const [hasAcceptedOsmTos] = useLocalStorageState<MapSettingsStorageState>("hasAcceptedOsmTos", {
    storageSync: true,
    defaultValue: {},
  });

  const { data: currentUser, isPending, isSuccess } = useCurrentUser();
  const geojson = useMemo(() => (markers ? getGeoJson(markers) : null), [markers]);

  if (isPending) {
    return <Spinner text="Loading..." />;
  }

  if (!isSuccess || !currentUser) {
    return null;
  }

  const style = hasAcceptedOsmTos[currentUser.username] ? osm : naturalEarth;

  const customAttribution =
    style === osm ? `<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>` : undefined;
  const initialOptions: maplibregl.MapOptions = {
    container: "map",
    style,
    dragRotate: false,
    trackResize: true,
    center: [0, 0],
    zoom: 3,
    maxZoom: 17,
    renderWorldCopies: true,
  };

  return (
    <MapContainer className="map" customAttribution={customAttribution} initialOptions={initialOptions}>
      {geojson ? <MarkersLayer geojson={geojson} /> : null}
    </MapContainer>
  );
};

export default Map;
