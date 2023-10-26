import { getClusterSize } from "./SiteMarker";

describe("getClusterSize", () => {
  it("should return 32 when count is less than 40% of maxCount", () => {
    expect(getClusterSize(20, 100)).toBe(32);
  });

  it("should return 48 when count is between 40% and 60% of maxCount", () => {
    expect(getClusterSize(50, 100)).toBe(48);
  });

  it("should return 58 when count is between 60% and 80% of maxCount", () => {
    expect(getClusterSize(70, 100)).toBe(58);
  });

  it("should return 88 when count is more than 80% of maxCount", () => {
    expect(getClusterSize(90, 100)).toBe(88);
  });

  it("should return 88 when count is equal to maxCount", () => {
    expect(getClusterSize(100, 100)).toBe(88);
  });
});
