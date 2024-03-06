export const isDev = process.env.NODE_ENV === "development";
export const useMockData = import.meta.env.VITE_USE_MOCK_DATA === "true";
export const basename = globalThis.__ROOT_PATH__ + import.meta.env.VITE_BASE_URL;
