import { useRef, useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { api } from "../services/api";
import { useLanguage } from "../contexts/LanguageContext";
import {
  Badge,
  DataTable,
  NumberValue,
  useCopy,
} from "../components/DataDisplay";
import { PageContainer, Panel, WarningBanner } from "../components/Page";
import { ResponseTimeline } from "../components/recommendations/ResponseTimeline";
import { AssistantTypingIndicator } from "../components/assistant/AssistantTypingIndicator";
import {
  assistantCategories,
  assistantExampleQuestions,
  type AssistantCategory,
} from "../data/assistantExampleQuestions";
import type { RecommendationResponse } from "../types/economic";
type Answer = {
  answer: string;
  calculation: string | null;
  warnings: string[];
  recommendation_plan: RecommendationResponse | null;
  values_used: Array<{
    indicator_code: string;
    indicator_name: string;
    year: number;
    value: number;
    source_file: string;
    worksheet: string;
  }>;
};
type Message = { question: string; answer: Answer };
export function EconomicAssistantPage() {
  const c = useCopy(),
    { language, direction } = useLanguage(),
    input = useRef<HTMLTextAreaElement>(null);
  const [question, setQuestion] = useState(""),
    [category, setCategory] = useState<AssistantCategory>("overview"),
    [messages, setMessages] = useState<Message[]>([]),
    [loading, setLoading] = useState(false),
    [error, setError] = useState("");
  const send = async (value = question) => {
    const clean = value.trim();
    if (!clean || loading) return;
    setLoading(true);
    setError("");
    setQuestion("");
    try {
      const previous=messages.at(-1)?.answer.values_used??[];
      const answer = (
        await api.post<Answer>("/api/assistant/query", {
          question: clean,
          language,
          last_indicator_codes:[...new Set(previous.map(value=>value.indicator_code))],
          last_year:previous.at(-1)?.year,
        })
      ).data;
      setMessages((old) => [...old, { question: clean, answer }]);
    } catch {
      setQuestion(clean);
      setError(
        c(
          "Impossible d’obtenir la réponse. Vérifiez la connexion puis réessayez.",
          "تعذر الحصول على الإجابة. تحقق من الاتصال ثم أعد المحاولة.",
        ),
      );
    } finally {
      setLoading(false);
    }
  };
  return (
    <PageContainer>
      <header className="rounded-3xl bg-gradient-to-br from-navy-950 to-mauritania-800 p-6 text-white shadow-card sm:p-8">
        <div className="flex items-center gap-3">
          <Sparkles />
          <span className="text-xs font-black tracking-widest">MEIP</span>
        </div>
        <h1 className="mt-3 text-3xl font-black">
          {c("Assistant économique MEIP", "المساعد الاقتصادي لمنصة MEIP")}
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-blue-100">
          {c(
            "Interrogez les données économiques mauritaniennes, comparez les secteurs, explorez les tendances ou analysez un scénario.",
            "استفسر عن البيانات الاقتصادية الموريتانية، وقارن القطاعات، واستكشف الاتجاهات أو حلّل سيناريو اقتصادياً.",
          )}
        </p>
      </header>
      <form
        className="mt-6 rounded-2xl border bg-white p-4 shadow-sm"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <label className="sr-only" htmlFor="assistant-question">
          {c("Votre question", "سؤالك")}
        </label>
        <textarea
          ref={input}
          id="assistant-question"
          dir={direction}
          required
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          className="min-h-28 w-full resize-y rounded-xl border border-slate-200 p-4 text-base outline-none focus:ring-2 focus:ring-mauritania-500"
          placeholder={c(
            "Posez une question sur l’économie mauritanienne…",
            "اطرح سؤالاً حول الاقتصاد الموريتاني…",
          )}
        />
        <div className="mt-3 flex justify-end">
          <button
            disabled={loading || !question.trim()}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-mauritania-700 px-5 py-3 font-bold text-white disabled:opacity-50"
          >
            <Send size={17} />
            {c("Envoyer", "إرسال")}
          </button>
        </div>
      </form>
      <section className="mt-6">
        <p className="rounded-xl bg-blue-50 p-4 text-sm leading-6 text-blue-900">
          {c(
            "Vous pouvez poser librement votre question. Les questions ci-dessous sont seulement des exemples de ce que l’assistant peut analyser.",
            "يمكنك طرح سؤالك بحرية. الأسئلة المعروضة أدناه ليست سوى أمثلة على ما يستطيع المساعد تحليله.",
          )}
        </p>
        <h2 className="mt-5 text-xl font-black">
          {c("Exemples de questions", "أمثلة على الأسئلة")}
        </h2>
        <div
          role="tablist"
          aria-label={c("Catégories d’exemples", "فئات الأمثلة")}
          className="mt-3 flex gap-2 overflow-x-auto pb-2"
        >
          {assistantCategories.map((item) => (
            <button
              type="button"
              role="tab"
              aria-selected={category === item.key}
              key={item.key}
              onClick={() => setCategory(item.key)}
              className={`min-h-11 shrink-0 rounded-full px-4 text-sm font-bold ${category === item.key ? "bg-navy-900 text-white" : "bg-white text-slate-700 ring-1 ring-slate-200"}`}
            >
              {c(item.fr, item.ar)}
            </button>
          ))}
        </div>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {assistantExampleQuestions
            .filter((item) => item.category === category)
            .map((item) => (
              <button
                type="button"
                key={item.fr}
                onClick={() => {
                  setQuestion(c(item.fr, item.ar));
                  input.current?.focus();
                }}
                className="min-h-20 rounded-2xl border bg-white p-4 text-start text-sm font-semibold shadow-sm hover:border-mauritania-400"
              >
                <small className="mb-2 block text-mauritania-700">
                  {c(
                    assistantCategories.find((x) => x.key === item.category)!
                      .fr,
                    assistantCategories.find((x) => x.key === item.category)!
                      .ar,
                  )}
                </small>
                {c(item.fr, item.ar)}
              </button>
            ))}
          <button
            type="button"
            onClick={() => input.current?.focus()}
            className="min-h-20 rounded-2xl border border-dashed border-mauritania-400 bg-mauritania-50 p-4 text-start text-sm font-black text-mauritania-800"
          >
            {c("Posez votre propre question", "اطرح سؤالك الخاص")}
          </button>
        </div>
      </section>
      <section aria-live="polite" className="mt-7 space-y-5">
        {messages.map((message, index) => (
          <div key={`${message.question}-${index}`}>
            <div className="ms-auto max-w-3xl rounded-2xl bg-mauritania-700 p-4 text-white">
              <p className="text-xs font-bold uppercase opacity-75">
                {c("Vous", "أنت")}
              </p>
              <p className="mt-1">{message.question}</p>
            </div>
            <Panel
              className="mt-3"
              title={c("Réponse de l’assistant", "إجابة المساعد")}
            >
              <p className="leading-8">{message.answer.answer}</p>
              {message.answer.recommendation_plan && (
                <>
                  <div className="my-5 flex items-center gap-3">
                    <strong>
                      {c("Risque du scénario", "مخاطر السيناريو")}
                    </strong>
                    <Badge tone="warning">
                      {message.answer.recommendation_plan.risk_level}
                    </Badge>
                  </div>
                  <ResponseTimeline
                    recommendations={
                      message.answer.recommendation_plan.recommendations
                    }
                  />
                </>
              )}
              {message.answer.values_used.length > 0 && (
                <>
                  <h3 className="mt-6 font-bold">
                    {c(
                      "Sources et valeurs utilisées",
                      "المصادر والقيم المستخدمة",
                    )}
                  </h3>
                  <div className="overflow-x-auto">
                    <DataTable
                      headers={[
                        c("Indicateur", "المؤشر"),
                        c("Année", "السنة"),
                        c("Valeur", "القيمة"),
                        c("Source", "المصدر"),
                      ]}
                      rows={message.answer.values_used.map((v) => [
                        v.indicator_name,
                        v.year,
                        <NumberValue value={v.value} />,
                        `${v.source_file} — ${v.worksheet}`,
                      ])}
                    />
                  </div>
                </>
              )}
              {message.answer.calculation && (
                <details className="mt-4">
                  <summary className="cursor-pointer font-bold">
                    {c("Calcul et méthode", "الحساب والمنهجية")}
                  </summary>
                  <pre className="mt-2 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-white">
                    {message.answer.calculation}
                  </pre>
                </details>
              )}
              {message.answer.warnings.length > 0 && (
                <div className="mt-4">
                  <WarningBanner title={c("Limites", "الحدود")}>
                    {message.answer.warnings.join(" ")}
                  </WarningBanner>
                </div>
              )}
            </Panel>
          </div>
        ))}
        {loading && <AssistantTypingIndicator />}
        {error && (
          <div
            role="alert"
            className="rounded-2xl border border-red-200 bg-red-50 p-4"
          >
            {error}
          </div>
        )}
      </section>
      <aside className="mt-8 rounded-2xl border bg-slate-50 p-5 text-sm leading-6">
        <h2 className="font-black">
          {c("Source et cadre de confiance", "المصدر وإطار الثقة")}
        </h2>
        <p className="mt-2">
          {c(
            "Les réponses chiffrées utilisent les comptes nationaux importés ANSADE/CN, à prix courants. Les simulations sont comptables et les prévisions sont expérimentales, jamais des projections officielles. Les données manquantes ne sont pas remplacées par zéro.",
            "تستخدم الإجابات الرقمية الحسابات الوطنية المستوردة وبالأسعار الجارية. المحاكاة محاسبية والتوقعات تجريبية وليست إسقاطات رسمية. ولا تستبدل القيم المفقودة بأصفار.",
          )}
        </p>
      </aside>
    </PageContainer>
  );
}
