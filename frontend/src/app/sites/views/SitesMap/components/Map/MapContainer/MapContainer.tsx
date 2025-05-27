import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

import { MapContextProvider } from "@/app/context/MapContext";

interface MapContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  initialOptions: maplibregl.MapOptions;
  customAttribution?: string;
}

/**
 * Sets up a map and adds it to the Context Provider.
 *
 * @note Changes to initialOptions are not reflected in the map after initialization.
 */
const MapContainer: React.FC<MapContainerProps> = ({ children, initialOptions, customAttribution, ...props }) => {
  const [map, setMap] = useState<maplibregl.Map | null>(null);

  useEffect(() => {
    const protocol = new Protocol();
    maplibregl.addProtocol("pmtiles", protocol.tile);
    return () => {
      maplibregl.removeProtocol("pmtiles");
    };
  }, []);

  const mapRef = useCallback(
    (node: HTMLDivElement | null) => {
      if (node !== null && map === null) {
        const newMap = new maplibregl.Map({ ...initialOptions, minZoom: 0, container: node });
        setMap(newMap);
      }
    },
    [map, initialOptions],
  );

  useEffect(() => {
    if (map) {
      map.on("load", () => {
        map.getCanvas().className += " is-visible";
      });
    }
  }, [map]);

  useEffect(() => {
    if (!map) return;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    return () => {
      map?.remove?.();
    };
  }, [map]);

  useEffect(() => {
    if (!map) return;
    map.addControl(new maplibregl.AttributionControl({ customAttribution }), "bottom-right");
  });

  return (
    <div ref={mapRef} {...props}>
      {map && <MapContextProvider map={map}>{children}</MapContextProvider>}
    </div>
  );
};

export default MapContainer;
