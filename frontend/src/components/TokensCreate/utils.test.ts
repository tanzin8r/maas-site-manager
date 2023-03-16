import { humanIntervalToISODuration } from "./utils";

describe("humanIntervalToISODuration", () => {
  it("returns a valid ISO duration string for hours and seconds", () => {
    expect(humanIntervalToISODuration("1 week 1 days 3 hours 30 seconds")).toEqual("P0Y0M8DT3H0M30S");
  });
});
