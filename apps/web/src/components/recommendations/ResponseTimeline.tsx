import type { Recommendation } from "../../types/economic";
import { Badge, useCopy } from "../DataDisplay";

const stages = [
  ["immediate", "Immédiat", "فوري", "0–3 mois", "0–3 أشهر"],
  ["stabilization", "Stabilisation", "استقرار", "3–12 mois", "3–12 شهراً"],
  ["recovery", "Reprise", "تعافٍ", "1–3 ans", "1–3 سنوات"],
  [
    "structural",
    "Résilience structurelle",
    "مرونة هيكلية",
    "Plus de 3 ans",
    "أكثر من 3 سنوات",
  ],
] as const;

const labels: Record<string, [string, string]> = {
  critical: ["Critique", "حرجة"],
  high: ["Élevée", "عالية"],
  medium: ["Moyenne", "متوسطة"],
  low: ["Faible", "منخفضة"],
  moderate: ["Modérée", "متوسطة"],
  public_authorities: ["Autorités publiques", "السلطات العامة"],
  sector_operators: ["Opérateurs sectoriels", "المشغلون القطاعيون"],
  financial_institutions: ["Institutions financières", "المؤسسات المالية"],
};

function RecommendationCard({ item }: { item: Recommendation }) {
  const c = useCopy();
  const local = (value: string) =>
    labels[value] ? c(labels[value][0], labels[value][1]) : value;
  return (
    <article className="rounded-2xl border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <h4 className="font-bold text-navy-950">
          {c(item.title_fr, item.title_ar)}
        </h4>
        <Badge
          tone={
            item.priority === "critical"
              ? "danger"
              : item.priority === "high"
                ? "warning"
                : "neutral"
          }
        >
          {local(item.priority)}
        </Badge>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-700">
        {c(item.reason_fr, item.reason_ar)}
      </p>
      <p className="mt-3 text-sm">
        <strong>{c("Objectif : ", "الهدف: ")}</strong>
        {c(item.expected_objective_fr, item.expected_objective_ar)}
      </p>
      <div className="mt-3 grid grid-cols-2 gap-2">
        {item.supporting_metrics.slice(0, 2).map((metric) => (
          <div
            className="rounded-lg bg-slate-50 p-2 text-xs"
            key={metric.label_fr}
          >
            <span>{c(metric.label_fr, metric.label_ar)}</span>
            <strong className="mt-1 block">
              {metric.value.toFixed(2)} {metric.unit}
            </strong>
          </div>
        ))}
      </div>
      <details className="mt-3 rounded-xl bg-slate-50 p-3 text-xs">
        <summary className="cursor-pointer font-bold text-mauritania-800">
          {c("Pourquoi cette recommandation ?", "لماذا هذه التوصية؟")}
        </summary>
        <p className="mt-2">
          <strong>{c("Confiance : ", "الثقة: ")}</strong>
          {local(item.confidence)} —{" "}
          {c(item.confidence_reason_fr, item.confidence_reason_ar)}
        </p>
        <p className="mt-2">
          <strong>{c("Mise en œuvre : ", "التنفيذ: ")}</strong>
          {c(
            item.implementation_steps_fr.join(" · "),
            item.implementation_steps_ar.join(" · "),
          )}
        </p>
        <p className="mt-2">
          <strong>{c("Responsables : ", "المسؤولون: ")}</strong>
          {item.responsible_actor_categories.map(local).join(", ")}
        </p>
        <p className="mt-2">
          <strong>{c("Seuil d’escalade : ", "عتبة التصعيد: ")}</strong>
          {c(item.escalation_trigger_fr, item.escalation_trigger_ar)}
        </p>
        <p className="mt-2 text-slate-500">
          {c(item.limitations_fr, item.limitations_ar)}
        </p>
        <details className="mt-2">
          <summary>{c("Codes techniques", "الرموز التقنية")}</summary>
          <code>{item.monitoring_indicators.join(", ")}</code>
        </details>
      </details>
    </article>
  );
}

export function ResponseTimeline({
  recommendations,
}: {
  recommendations: Recommendation[];
}) {
  const c = useCopy();
  return (
    <div
      data-testid="recommendation-timeline"
      className="grid gap-5 lg:grid-cols-4"
    >
      {stages.map(([key, fr, ar, periodFr, periodAr], index) => {
        const items = recommendations.filter(
          (item) => item.time_horizon === key,
        );
        return (
          <section key={key}>
            <div className="mb-4 flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-full bg-navy-900 font-black text-white">
                {index + 1}
              </span>
              <div>
                <h3 className="font-black text-navy-950">{c(fr, ar)}</h3>
                <p className="text-xs text-slate-500">
                  {c(periodFr, periodAr)}
                </p>
              </div>
            </div>
            <div className="grid gap-3">
              {items.map((item) => (
                <RecommendationCard item={item} key={item.code} />
              ))}
              {!items.length && (
                <p className="rounded-xl bg-slate-50 p-3 text-xs text-slate-500">
                  {c(
                    "Aucune action à ce stade.",
                    "لا يوجد إجراء في هذه المرحلة.",
                  )}
                </p>
              )}
            </div>
          </section>
        );
      })}
    </div>
  );
}
