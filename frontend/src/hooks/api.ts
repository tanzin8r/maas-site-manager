import { useQuery } from "react-query";
import { getSites } from "../api/handlers";
import { Sites } from "../api/types";

export const useSitesQuery = () => useQuery<Sites>("/api/sites", getSites);
