import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { LanguageProvider } from "../contexts/LanguageContext";
import i18n from "../i18n";
import { SimulationAndReactionPage } from "../pages/SimulationAndReactionPage";
import * as stress from "../services/stressTest";

vi.mock("../services/stressTest");
const points = (first: number | null, last: number | null) => [
  { year: 2023, value: first },
  { year: 2024, value: last },
];
const pageData = {
  sectors: [],
  years: [2023, 2024],
  composition: [],
  gdpSeries: points(1000, 1200),
  seriesByCode: {
    primary_sector: points(280, 300),
    secondary_sector: points(350, 400),
    tertiary_sector: points(370, 400),
    snim_iron: points(90, 100),
    gold_copper: points(40, 50),
    oil_gas_extraction: points(10, 20),
    agriculture_forestry: points(80, 100),
    fishing: points(40, 50),
    manufacturing: points(180, 200),
    commerce: points(220, 250),
  },
};
function setup(data = pageData) {
  vi.mocked(stress.loadSimulationPageData).mockResolvedValue(data);
}
function renderPage() {
  return render(
    <LanguageProvider>
      <MemoryRouter>
        <SimulationAndReactionPage />
      </MemoryRouter>
    </LanguageProvider>,
  );
}

describe("latest-year shock and diversification simulator", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    await i18n.changeLanguage("fr");
    setup();
  });
  it("automatically uses the latest GDP year and has no year selector", async () => {
    renderPage();
    expect(
      await screen.findByRole("heading", {
        name: "Simulateur de choc et de diversification",
      }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("latest-year")).toHaveTextContent("2024");
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    expect(screen.getByTestId("base-gdp-kpi")).toHaveTextContent(/1.?200/);
    expect(stress.loadSimulationPageData).toHaveBeenCalledTimes(1);
  });
  it("shows an initial skeleton while the source series are loading", () => {
    vi.mocked(stress.loadSimulationPageData).mockReturnValue(
      new Promise(() => {}),
    );
    renderPage();
    expect(screen.getByTestId("chart-skeleton")).toBeInTheDocument();
    expect(screen.getAllByTestId("kpi-skeleton")).toHaveLength(3);
  });
  it("recalculates a mining loss locally without making simulation requests", async () => {
    renderPage();
    const slider = await screen.findByTestId("mining-snim_iron");
    fireEvent.change(slider, { target: { value: "-50" } });
    expect(screen.getByTestId("mining-losses")).toHaveTextContent(/50/);
    expect(screen.getByTestId("scenario-gdp-kpi")).toHaveTextContent(/1.?150/);
    expect(screen.getByTestId("variation-kpi")).toHaveTextContent(/4[,.]17%/);
    expect(stress.simulateSingle).not.toHaveBeenCalled();
    expect(stress.loadImpactPreview).not.toHaveBeenCalled();
  });
  it("adds diversification gains and updates the chart summary immediately", async () => {
    renderPage();
    const slider = await screen.findByTestId("policy-manufacturing");
    fireEvent.change(slider, { target: { value: "10" } });
    expect(screen.getByTestId("diversification-gains")).toHaveTextContent(/20/);
    expect(screen.getByTestId("scenario-gdp-kpi")).toHaveTextContent(/1.?220/);
    expect(screen.getByTestId("chart-summary")).toHaveTextContent(
      /Secondaire: 400 \/ 420/,
    );
    expect(screen.getByTestId("gdp-impact-bar-chart")).toBeInTheDocument();
  });
  it("combines agriculture and fishing for the primary policy base", async () => {
    renderPage();
    const slider = await screen.findByTestId("policy-agriculture_fishing");
    fireEvent.change(slider, { target: { value: "10" } });
    expect(screen.getByTestId("diversification-gains")).toHaveTextContent(/15/);
    expect(screen.getByTestId("chart-summary")).toHaveTextContent(
      /Primaire: 300 \/ 315/,
    );
  });
  it("falls back to the latest common valid year", async () => {
    setup({
      ...pageData,
      seriesByCode: {
        ...pageData.seriesByCode,
        oil_gas_extraction: points(10, null),
      },
    });
    renderPage();
    expect(await screen.findByTestId("mining-oil_gas_extraction")).toBeEnabled();
    expect(screen.getByTestId("latest-year")).toHaveTextContent("2023");
  });
  it("supports Arabic RTL with translated decision labels", async () => {
    await i18n.changeLanguage("ar");
    renderPage();
    expect(
      await screen.findByRole("heading", {
        name: "محاكي الصدمات والتنويع الاقتصادي",
      }),
    ).toBeInTheDocument();
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
    expect(screen.getByTestId("latest-year")).toHaveTextContent(
      "بيانات سنة الأساس",
    );
    expect(screen.getByText("خسائر التعدين")).toBeInTheDocument();
  });
  it.each([320,375,390,430,768,1280])("keeps the simulator responsive at %ipx", async (width) => {
    Object.defineProperty(window, "innerWidth", {
      value: width,
      writable: true,
      configurable: true,
    });
    renderPage();
    const layout = await screen.findByTestId("simulator-layout");
    expect(layout.children[0]).toContainElement(
      screen.getByTestId("mining-snim_iron"),
    );
    expect(layout.children[1]).toContainElement(
      screen.getByTestId("base-gdp-kpi"),
    );
    expect(layout.closest("main")).toHaveClass("overflow-x-clip");
    expect(screen.getByTestId("mining-snim_iron")).toHaveClass("h-11","w-full");
  });
  it("shows a retryable source error", async () => {
    vi.mocked(stress.loadSimulationPageData).mockRejectedValue(
      new Error("network unavailable"),
    );
    renderPage();
    expect(
      await screen.findByText("Impossible de charger ces données"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Réessayer" }),
    ).toBeInTheDocument();
  });
});
