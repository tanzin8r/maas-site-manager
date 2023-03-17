import { customParamSerializer, getTimeByUTCOffset, getTimezoneUTCString, parseSearchTextToQueryParams } from "./utils";

describe("parseSearchTextToQueryParams tests", () => {
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
});

describe("customParamSerializer", () => {
  it("should serialize params normally if just params are provided", () => {
    const params = { page: "1", size: "20" };
    const serialized = customParamSerializer(params);
    const expectedResult = "page=1&size=20";
    expect(serialized).toBe(expectedResult);
  });

  it("should be compatible with already serialized queryText", () => {
    const params = { page: "1", size: "20" };
    const serializedQueryText = "country=cuba";
    const serialized = customParamSerializer(params, serializedQueryText);
    const expectedResult = `page=1&size=20&${serializedQueryText}`;
    expect(serialized).toBe(expectedResult);
  });
});

describe("getTimezoneUTCString", () => {
  it("should return the correct positive UTC string", () => {
    const offset = 2;
    const result = getTimezoneUTCString(offset);
    expect(result).toBe("+02:00");
  });

  it("should return the correct negative UTC string", () => {
    const offset = -5;
    const result = getTimezoneUTCString(offset);
    expect(result).toBe("-05:00");
  });

  it("should return the correct UTC string for '0' offset", () => {
    const offset = 0;
    const result = getTimezoneUTCString(offset);
    expect(result).toBe("+00:00");
  });
});

describe("getTimeByUTCOffset", () => {
  it("should display correct positive time offset", () => {
    const date = new Date("2000-01-01T12:00:00Z");
    const offset = 2;
    const result = getTimeByUTCOffset(date, offset);
    expect(result).toBe("14:00");
  });
  it("should display correct negative time offset", () => {
    const date = new Date("2000-01-01T12:00:00Z");
    const offset = -2;
    const result = getTimeByUTCOffset(date, offset);
    expect(result).toBe("10:00");
  });
});
