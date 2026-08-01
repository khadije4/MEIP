import { useLanguage } from "../../contexts/LanguageContext";
import type { DiversificationKey } from "../../utils/latestYearSimulation";
import { useCopy } from "../DataDisplay";

const definitions: Array<{ key: DiversificationKey; fr: string; ar: string }> =
  [
    {
      key: "agriculture_fishing",
      fr: "Agriculture & Pêche",
      ar: "الزراعة والصيد",
    },
    {
      key: "manufacturing",
      fr: "Industrie manufacturière",
      ar: "الصناعة التحويلية",
    },
    {
      key: "services_commerce",
      fr: "Services & Commerce",
      ar: "الخدمات والتجارة",
    },
  ];
export function DiversificationPolicyCard({
  values,
  rates,
  onRate,
}: {
  values: Record<DiversificationKey, number | null>;
  rates: Record<DiversificationKey, number>;
  onRate: (key: DiversificationKey, value: number) => void;
}) {
  const c = useCopy();
  const { language } = useLanguage();
  const nf = new Intl.NumberFormat(language === "ar" ? "ar-MR" : "fr-MR", {
    maximumFractionDigits: 2,
  });
  return (
    <section className="rounded-3xl border border-emerald-200 bg-white p-5 shadow-card sm:p-6">
      <div className="mb-5">
        <p className="text-xs font-black uppercase tracking-widest text-emerald-700">
          {c("Résilience", "المرونة")}
        </p>
        <h2 className="mt-1 text-xl font-black">
          {c("Politiques de diversification", "سياسات التنويع الاقتصادي")}
        </h2>
      </div>
      <div className="grid gap-6">
        {definitions.map((item) => {
          const unavailable = values[item.key] == null,
            value = rates[item.key];
          return (
            <label
              className={`grid gap-2 ${unavailable ? "opacity-55" : ""}`}
              key={item.key}
            >
              <span className="flex items-center justify-between gap-3 text-sm font-bold">
                <span>{c(item.fr, item.ar)}</span>
                <output
                  htmlFor={`policy-${item.key}`}
                  className="rounded-full bg-emerald-50 px-2.5 py-1 tabular-nums text-emerald-700"
                >
                  +{value}%
                </output>
              </span>
              <input
                id={`policy-${item.key}`}
                data-testid={`policy-${item.key}`}
                disabled={unavailable}
                type="range"
                min="0"
                max="50"
                step="1"
                value={value}
                onChange={(event) => onRate(item.key, +event.target.value)}
                aria-valuetext={c(`${value} pour cent`, `نسبة ${value} بالمئة`)}
                className="h-11 w-full accent-emerald-600 outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed"
              />
              {unavailable ? (
                <span className="text-xs font-semibold text-red-700">
                  {c("Donnée indisponible", "البيانات غير متاحة")}
                </span>
              ) : (
                <span className="text-xs text-slate-500">
                  {c("Base", "الأساس")}: {nf.format(values[item.key]!)}{" "}
                  {c("millions MRU", "مليون أوقية")}
                </span>
              )}
            </label>
          );
        })}
      </div>
      <p className="mt-5 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-600">
        {c(
          "Agriculture & Pêche additionne agriculture/sylviculture et pêche. Services & Commerce utilise la série Commerce afin d’éviter d’appliquer le même taux à tout le tertiaire.",
          "تجمع الزراعة والصيد بين الزراعة/الغابات والصيد. وتستخدم الخدمات والتجارة سلسلة التجارة لتجنب تطبيق المعدل نفسه على القطاع الثالثي بأكمله.",
        )}
      </p>
    </section>
  );
}
