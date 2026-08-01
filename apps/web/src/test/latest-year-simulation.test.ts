import {
  calculateLatestYearScenario,
  detectLatestAvailableYear,
  detectLatestCommonYear,
  latestValue,
} from "../utils/latestYearSimulation";

describe("percent-based central scenario contract", () => {
  it("keeps the documented neutral scenario exactly neutral", () => {
    const result = calculateLatestYearScenario({
      baselineGdp: 429701.3,
      shockAdjustments: [
        { indicatorCode: "snim_iron", baseValue: 100, adjustmentPercent: 0 },
      ],
      diversificationAdjustments: [
        {
          indicatorCode: "manufacturing",
          baseValue: 200,
          adjustmentPercent: 0,
        },
      ],
    });
    expect(result).toMatchObject({
      baselineGdp: 429701.3,
      totalLosses: 0,
      totalGains: 0,
      netImpact: 0,
      simulatedGdp: 429701.3,
      variationPercent: 0,
    });
  });
  it.each([
    ["loss",1000,[{indicatorCode:"sector",baseValue:200,adjustmentPercent:-50}],[],{totalLosses:100,totalGains:0,netImpact:-100,simulatedGdp:900,variationPercent:-10}],
    ["gain",1000,[],[{indicatorCode:"sector",baseValue:250,adjustmentPercent:20}],{totalLosses:0,totalGains:50,netImpact:50,simulatedGdp:1050,variationPercent:5}],
    ["combined",1000,[{indicatorCode:"loss",baseValue:200,adjustmentPercent:-50}],[{indicatorCode:"gain",baseValue:200,adjustmentPercent:20}],{totalLosses:100,totalGains:40,netImpact:-60,simulatedGdp:940,variationPercent:-6}],
  ])("calculates the required %s scenario",(_name,baselineGdp,shockAdjustments,diversificationAdjustments,expected)=>{
    expect(calculateLatestYearScenario({baselineGdp:baselineGdp as number,shockAdjustments,diversificationAdjustments})).toMatchObject(expected)
  })
});

const input = {
  baselineGdp: 1200,
  shockAdjustments: [
    { indicatorCode: "snim_iron", baseValue: 100, adjustmentPercent: -50 },
  ],
  diversificationAdjustments: [
    { indicatorCode: "manufacturing", baseValue: 200, adjustmentPercent: 10 },
  ],
};
describe("latest-year simulation calculations", () => {
  it("detects the maximum common valid simulator year",()=>expect(detectLatestCommonYear([[{year:2023,value:1},{year:2024,value:2}],[{year:2023,value:3},{year:2024,value:null}]])).toBe(2023));
  it("detects the most recent non-missing GDP observation", () => {
    const series = [
      { year: 2023, value: 10 },
      { year: 2024, value: null },
      { year: 2022, value: 9 },
    ];
    expect(detectLatestAvailableYear(series)).toBe(2023);
    expect(latestValue(series, 2024)).toBeNull();
  });
  it("combines losses and gains without rounding inputs", () => {
    const result = calculateLatestYearScenario(input);
    expect(result.totalLosses).toBe(50);
    expect(result.totalGains).toBe(20);
    expect(result.netImpact).toBe(-30);
    expect(result.simulatedGdp).toBe(1170);
    expect(result.variationPercent).toBeCloseTo(-2.5);
  });
  it("keeps missing values unavailable rather than silently zero-filling", () => {
    const result = calculateLatestYearScenario({
      ...input,
      shockAdjustments: [
        {
          indicatorCode: "oil_gas_extraction",
          baseValue: null,
          adjustmentPercent: 0,
        },
      ],
    });
    expect(result.unavailableIndicatorCodes).toContain("oil_gas_extraction");
    expect(result.sectorResults).toHaveLength(1);
  });
  it("rejects percentages outside the documented slider bounds", () => {
    expect(() =>
      calculateLatestYearScenario({
        ...input,
        shockAdjustments: [
          {
            indicatorCode: "snim_iron",
            baseValue: 100,
            adjustmentPercent: -81,
          },
        ],
      }),
    ).toThrow(RangeError);
    expect(() =>
      calculateLatestYearScenario({
        ...input,
        diversificationAdjustments: [
          {
            indicatorCode: "manufacturing",
            baseValue: 200,
            adjustmentPercent: 51,
          },
        ],
      }),
    ).toThrow(RangeError);
  });
  it("rejects parent-child and alias duplication", () => {
    expect(() =>
      calculateLatestYearScenario({
        ...input,
        shockAdjustments: [
          {
            indicatorCode: "secondary_sector",
            baseValue: 400,
            adjustmentPercent: -10,
          },
          {
            indicatorCode: "manufacturing",
            parentIndicatorCode: "secondary_sector",
            baseValue: 200,
            adjustmentPercent: -10,
          },
        ],
      }),
    ).toThrow(/overlap/);
    expect(() =>
      calculateLatestYearScenario({
        ...input,
        shockAdjustments: [
          {
            indicatorCode: "primary_sector",
            baseValue: 300,
            adjustmentPercent: -10,
          },
          {
            indicatorCode: "agriculture_fishing_forestry",
            canonicalIndicatorCode: "primary_sector",
            baseValue: 300,
            adjustmentPercent: -10,
          },
        ],
      }),
    ).toThrow(/Duplicate/);
  });
});
