import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Landmark,
  RotateCcw,
  Scale,
} from "lucide-react";
import { GdpImpactBarChart } from "../components/charts/GdpImpactBarChart";
import { GdpShockWaterfallChart } from "../components/charts/GdpShockWaterfallChart";
import {
  CurrentPriceWarning,
  Metadata,
  useCopy,
} from "../components/DataDisplay";
import { SectionErrorState } from "../components/ErrorStates";
import { PageLoadingState } from "../components/LoadingStates";
import {
  PageContainer,
  PageHeader,
  Panel,
  StatePanel,
  WarningBanner,
} from "../components/Page";
import { DiversificationPolicyCard } from "../components/simulation/DiversificationPolicyCard";
import { MiningShockCard } from "../components/simulation/MiningShockCard";
import { useLanguage } from "../contexts/LanguageContext";
import { loadSimulationPageData } from "../services/stressTest";
import {
  buildLatestYearSimulationView,
  detectLatestCommonYear,
  latestValue,
  type DiversificationKey,
  type MiningKey,
} from "../utils/latestYearSimulation";

type PageData = Awaited<ReturnType<typeof loadSimulationPageData>>;
const initialMiningRates: Record<MiningKey, number> = {
  snim_iron: 0,
  gold_copper: 0,
  oil_gas_extraction: 0,
};
const initialDiversificationRates: Record<DiversificationKey, number> = {
  agriculture_fishing: 0,
  manufacturing: 0,
  services_commerce: 0,
};

function sumAvailable(left: number | null, right: number | null) {
  return left == null || right == null ? null : left + right;
}

export function SimulationAndReactionPage() {
  const c = useCopy();
  const { language } = useLanguage();
  const [loaded, setLoaded] = useState<PageData | null>(null),
    [initialError, setInitialError] = useState(""),
    [reload, setReload] = useState(0);
  const [miningRates, setMiningRates] = useState(initialMiningRates),
    [diversificationRates, setDiversificationRates] = useState(
      initialDiversificationRates,
    );
  useEffect(() => {
    let active = true;
    setLoaded(null);
    setInitialError("");
    void loadSimulationPageData()
      .then((result) => active && setLoaded(result))
      .catch(
        (reason) =>
          active &&
          setInitialError(
            reason instanceof Error ? reason.message : String(reason),
          ),
      );
    return () => {
      active = false;
    };
  }, [reload]);
  const latestYear = useMemo(() => {
    if (!loaded) return null;
    try {
      return detectLatestCommonYear([loaded.gdpSeries,...['primary_sector','secondary_sector','tertiary_sector','snim_iron','gold_copper','oil_gas_extraction','agriculture_forestry','fishing','manufacturing','commerce'].map(code=>loaded.seriesByCode[code]??[])]);
    } catch { return null; }
  }, [loaded]);
  const values = useMemo(() => {
    if (!loaded || latestYear == null) return null;
    const get = (code: string) =>
      latestValue(loaded.seriesByCode[code], latestYear);
    return {
      baseGdp: latestValue(loaded.gdpSeries, latestYear),
      primarySector: get("primary_sector"),
      secondarySector: get("secondary_sector"),
      tertiarySector: get("tertiary_sector"),
      mining: {
        snim_iron: get("snim_iron"),
        gold_copper: get("gold_copper"),
        oil_gas_extraction: get("oil_gas_extraction"),
      } as Record<MiningKey, number | null>,
      diversification: {
        agriculture_fishing: sumAvailable(
          get("agriculture_forestry"),
          get("fishing"),
        ),
        manufacturing: get("manufacturing"),
        services_commerce: get("commerce"),
      } as Record<DiversificationKey, number | null>,
    };
  }, [latestYear, loaded]);
  const result = useMemo(
    () =>
      !values || values.baseGdp == null
        ? null
        : (() => {
            const view = buildLatestYearSimulationView({
            baselineGdp: values.baseGdp,
            primarySector: values.primarySector,
            secondarySector: values.secondarySector,
            tertiarySector: values.tertiarySector,
            miningValues: values.mining,
            miningPercents: miningRates,
            diversificationValues: values.diversification,
            diversificationPercents: diversificationRates,
          });
            return {...view.simulation,scenarioGdp:view.simulation.simulatedGdp,variationAbsolute:view.simulation.netImpact,totalMiningLosses:view.simulation.totalLosses,totalDiversificationGains:view.simulation.totalGains,categories:view.categories};
          })(),
    [diversificationRates, miningRates, values],
  );
  const nf = new Intl.NumberFormat(language === "ar" ? "ar-MR" : "fr-MR", {
    maximumFractionDigits: 2,
  });
  const money = (value: number | null | undefined) =>
    value == null ? "—" : nf.format(value);
  const signed = (value: number) =>
    `${value > 0 ? "+" : value < 0 ? "−" : ""}${nf.format(Math.abs(value))}`;
  const setMining = (key: MiningKey, value: number) =>
    setMiningRates((old) => ({ ...old, [key]: value }));
  const setDiversification = (key: DiversificationKey, value: number) =>
    setDiversificationRates((old) => ({ ...old, [key]: value }));
  const reset = () => {
    setMiningRates(initialMiningRates);
    setDiversificationRates(initialDiversificationRates);
  };
  if (!loaded && !initialError) return <PageLoadingState />;
  if (initialError)
    return (
      <PageContainer>
        <SectionErrorState
          details={initialError}
          onRetry={() => setReload((value) => value + 1)}
        />
      </PageContainer>
    );
  if (latestYear == null || !values || !result)
    return (
      <PageContainer>
        <StatePanel
          state="empty"
          title={c("PIB indisponible", "بيانات الناتج غير متاحة")}
          description={c(
            "Aucune observation du PIB ne permet de lancer la simulation.",
            "لا توجد ملاحظة للناتج تسمح بتشغيل المحاكاة.",
          )}
        />
      </PageContainer>
    );
  const variationTone =
    result.variationAbsolute < 0
      ? "text-red-700"
      : result.variationAbsolute > 0
        ? "text-emerald-700"
        : "text-slate-950";
  return (
    <PageContainer>
      <PageHeader
        eyebrow={c("Cockpit de décision", "قمرة قيادة القرار")}
        title={c(
          "Simulateur de choc et de diversification",
          "محاكي الصدمات والتنويع الاقتصادي",
        )}
        description={c(
          "Testez instantanément l’effet comptable de chocs miniers et de politiques de diversification sur la dernière année disponible.",
          "اختبر فوراً الأثر المحاسبي لصدمات التعدين وسياسات التنويع على آخر سنة متاحة.",
        )}
        actions={
          <button
            type="button"
            onClick={reset}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-bold"
          >
            <RotateCcw size={17} />
            {c("Réinitialiser", "إعادة الضبط")}
          </button>
        }
      />
      <div className="mt-5 grid gap-4 sm:grid-cols-[auto_1fr] sm:items-center">
        <p
          data-testid="latest-year"
          className="w-fit rounded-full bg-mauritania-50 px-4 py-2 text-sm font-black text-mauritania-800"
        >
          {c("Données de référence", "بيانات سنة الأساس")}: {latestYear}
        </p>
        <CurrentPriceWarning />
      </div>
      <section
        data-testid="simulator-layout"
        className="mt-6 grid min-w-0 gap-6 lg:grid-cols-[minmax(300px,0.86fr)_minmax(0,1.4fr)]"
      >
        <div className="grid min-w-0 content-start gap-6">
          <MiningShockCard
            values={values.mining}
            rates={miningRates}
            onRate={setMining}
          />
          <DiversificationPolicyCard
            values={values.diversification}
            rates={diversificationRates}
            onRate={setDiversification}
          />
        </div>
        <div className="grid min-w-0 content-start gap-6">
          <section
            className="grid gap-3 sm:grid-cols-3"
            aria-label={c("Résultats principaux", "النتائج الرئيسية")}
          >
            <article
              data-testid="base-gdp-kpi"
              className="rounded-2xl border bg-white p-5 shadow-card"
            >
              <Landmark className="text-slate-500" size={20} />
              <p className="mt-3 text-sm font-semibold text-slate-500">
                {c("PIB de base", "الناتج الأساسي")}
              </p>
              <p className="mt-1 text-2xl font-black tabular-nums">
                {money(result.baselineGdp)}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                {c("millions MRU", "مليون أوقية")}
              </p>
            </article>
            <article
              data-testid="scenario-gdp-kpi"
              className="rounded-2xl border border-mauritania-200 bg-mauritania-50/40 p-5 shadow-card"
            >
              <Scale className="text-mauritania-700" size={20} />
              <p className="mt-3 text-sm font-semibold text-slate-600">
                {c("PIB simulé", "الناتج المحلي بعد المحاكاة")}
              </p>
              <p className="mt-1 text-2xl font-black tabular-nums text-mauritania-800">
                {money(result.scenarioGdp)}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                {c("millions MRU", "مليون أوقية")}
              </p>
            </article>
            <article
              data-testid="variation-kpi"
              className="rounded-2xl border bg-white p-5 shadow-card"
            >
              {result.variationAbsolute < 0 ? (
                <ArrowDownRight className="text-red-600" size={20} />
              ) : (
                <ArrowUpRight
                  className={
                    result.variationAbsolute > 0
                      ? "text-emerald-600"
                      : "text-slate-500"
                  }
                  size={20}
                />
              )}
              <p className="mt-3 text-sm font-semibold text-slate-500">
                {c("Variation", "التغير")}
              </p>
              <p
                className={`mt-1 text-2xl font-black tabular-nums ${variationTone}`}
              >
                {signed(result.variationPercent)}%
              </p>
              <p className="mt-1 text-xs tabular-nums text-slate-500">
                {signed(result.variationAbsolute)}{" "}
                {c("millions MRU", "مليون أوقية")}
              </p>
            </article>
          </section>
          <section
            className="grid gap-3 sm:grid-cols-3"
            aria-label={c("Décomposition de l’impact", "تفصيل الأثر")}
          >
            <article
              data-testid="mining-losses"
              className="rounded-2xl border border-red-100 bg-red-50/60 p-4"
            >
              <p className="text-xs font-bold text-red-700">
                {c("Pertes minières", "خسائر التعدين")}
              </p>
              <p className="mt-1 text-xl font-black tabular-nums text-red-800">
                −{money(result.totalMiningLosses)}
              </p>
            </article>
            <article
              data-testid="diversification-gains"
              className="rounded-2xl border border-emerald-100 bg-emerald-50/60 p-4"
            >
              <p className="text-xs font-bold text-emerald-700">
                {c("Gains de diversification", "مكاسب التنويع")}
              </p>
              <p className="mt-1 text-xl font-black tabular-nums text-emerald-800">
                +{money(result.totalDiversificationGains)}
              </p>
            </article>
            <article
              data-testid="net-impact"
              className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
            >
              <p className="text-xs font-bold text-slate-600">
                {c("Impact net", "الأثر الصافي")}
              </p>
              <p
                className={`mt-1 text-xl font-black tabular-nums ${variationTone}`}
              >
                {signed(result.netImpact)}
              </p>
            </article>
          </section>
          {result.netImpact===0&&<p className="rounded-xl bg-slate-50 p-3 text-center text-sm font-bold">{c("Aucun choc appliqué","لم تُطبّق أي صدمة")}</p>}
          <Panel
            title={c("Impact sur le PIB", "الأثر على الناتج المحلي")}
            subtitle={c(
              `Comparaison directe par grand groupe en ${latestYear}.`,
              `مقارنة مباشرة حسب المجموعة الكبرى في ${latestYear}.`,
            )}
          >
            <GdpImpactBarChart
              categories={result.categories}
              year={latestYear}
            />
            <p className="mt-3 text-sm leading-6 text-slate-500">
              {c(
                "Simulation basée sur la dernière année disponible des comptes nationaux. Les résultats représentent un impact comptable direct. « Minerais » additionne uniquement Fer (SNIM), Or & Cuivre et Pétrole & Gaz lorsque les trois observations sont disponibles.",
                "تعتمد المحاكاة على أحدث سنة متاحة من الحسابات الوطنية، وتمثل النتائج أثراً محاسبياً مباشراً. تجمع فئة «المعادن» فقط الحديد (سنيم) والذهب والنحاس والنفط والغاز عند توفر الملاحظات الثلاث.",
              )}
            </p>
            <Metadata />
          </Panel>
          <Panel title={c("Décomposition en cascade", "التفسير المتدرج للأثر")}>
            <GdpShockWaterfallChart baselineGdp={result.baselineGdp} directLoss={result.totalLosses} compensationGain={result.totalGains} simulatedGdp={result.baselineGdp-result.totalLosses}/>
          </Panel>
        </div>
      </section>
      <div className="mt-6">
        <WarningBanner title={c("Limite méthodologique", "قيد منهجي")}>
          {c(
            "Cette simulation applique directement chaque taux à la valeur observée du secteur. Elle ne constitue ni une prévision macroéconomique ni une estimation des effets indirects, des prix, de l’emploi ou des finances publiques.",
            "تطبق هذه المحاكاة كل معدل مباشرة على القيمة المرصودة للقطاع. وهي ليست توقعاً اقتصادياً كلياً ولا تقديراً للآثار غير المباشرة أو الأسعار أو التشغيل أو المالية العامة.",
          )}
        </WarningBanner>
      </div>
    </PageContainer>
  );
}
