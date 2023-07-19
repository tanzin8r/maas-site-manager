import type { SortingState } from "@tanstack/react-table";

import {
  customParamSerializer,
  getTimezoneUTCString,
  parseSearchTextToQueryParams,
  getTimeInTimezone,
  formatDistanceToNow,
  getSortBy,
} from "./utils";

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

it('should modify search params from "label:value" to "label=value"', () => {
  const searchText = "country:cuba";
  const queryParams = parseSearchTextToQueryParams(searchText);
  expect(queryParams.includes(":")).toBe(false);
  expect(queryParams.includes("=")).toBe(true);
  expect(queryParams).toBe("country=cuba");
});

it("should modify multiple search params", () => {
  const searchText = "country:cuba city:paris";
  const queryParams = parseSearchTextToQueryParams(searchText);
  const expectedResponse = "country=cuba&city=paris";
  expect(queryParams).toBe(expectedResponse);
});

it("should serialize params normally if just params are provided", () => {
  const params = { page: "1", size: "20", sort_by: "name-asc" };
  const serialized = customParamSerializer(params);
  const expectedResult = "page=1&size=20&sort_by=name-asc";
  expect(serialized).toBe(expectedResult);
});

it("should be compatible with already serialized queryText", () => {
  const params = { page: "1", size: "20" };
  const serializedQueryText = "country=cuba";
  const serialized = customParamSerializer(params, serializedQueryText);
  const expectedResult = `page=1&size=20&${serializedQueryText}`;
  expect(serialized).toBe(expectedResult);
});

it("should skip parameters with null values", () => {
  const params = { page: "1", size: "20", sort_by: null };
  const serialized = customParamSerializer(params);
  const expectedResult = `page=1&size=20`;
  expect(serialized).toBe(expectedResult);
});

[
  ["Canada/Newfoundland", "-2:30"],
  ["UTC", ""],
  ["Europe/London", "+1"],
].forEach(([timezone, expected]) => {
  it(`returns ${expected} for ${timezone}`, () => {
    const result = getTimezoneUTCString(timezone);
    expect(result).toBe(expected);
  });
});

[
  ["Canada/Newfoundland", "09:30"],
  ["UTC", "12:00"],
  ["Europe/Warsaw", "14:00"],
  ["Europe/London", "13:00"],
].forEach(([timezone, expected]) => {
  it(`returns ${expected} for ${timezone}`, () => {
    const result = getTimeInTimezone(new Date("2000-01-01T12:00:00Z"), timezone);
    expect(result).toBe(expected);
  });
});

const date = new Date("Fri Apr 21 2023 12:00:00 GMT+0100 (GMT)");
[
  ["2023-04-21T10:30:00.000Z", "30 minutes ago"],
  ["2023-04-21T11:15:00.000Z", "in 15 minutes"],
].forEach(([time, expected]) => {
  it(`returns ${expected} time distance for ${time}`, () => {
    vi.setSystemTime(date);
    const result = formatDistanceToNow(time);
    expect(result).toBe(expected);
  });
});

const sortingState: SortingState = [{ id: "name", desc: false }];

it("returns a sort key as a string", () => {
  const sortKey = getSortBy(sortingState);
  expect(sortKey).toStrictEqual("name-asc");
});
