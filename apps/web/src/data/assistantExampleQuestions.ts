export type AssistantCategory =
  | "overview"
  | "gdp"
  | "sectors"
  | "mining"
  | "trade"
  | "comparisons"
  | "forecasts"
  | "scenarios"
  | "methodology";
export type AssistantExample = {
  category: AssistantCategory;
  fr: string;
  ar: string;
};
export const assistantCategories: Array<{
  key: AssistantCategory;
  fr: string;
  ar: string;
}> = [
  { key: "overview", fr: "Vue générale", ar: "نظرة عامة" },
  { key: "gdp", fr: "PIB", ar: "الناتج المحلي" },
  { key: "sectors", fr: "Secteurs", ar: "القطاعات" },
  { key: "mining", fr: "Mines", ar: "التعدين" },
  { key: "trade", fr: "Commerce extérieur", ar: "التجارة الخارجية" },
  { key: "comparisons", fr: "Comparaisons", ar: "المقارنات" },
  { key: "forecasts", fr: "Prévisions", ar: "التوقعات" },
  { key: "scenarios", fr: "Scénarios", ar: "السيناريوهات" },
  { key: "methodology", fr: "Méthodologie", ar: "المنهجية" },
];
export const assistantExampleQuestions: AssistantExample[] = [
  {
    category: "overview",
    fr: "Que montrent les données économiques disponibles ?",
    ar: "ماذا تظهر البيانات الاقتصادية المتاحة؟",
  },
  {
    category: "overview",
    fr: "Quelle est la dernière année disponible ?",
    ar: "ما آخر سنة متاحة؟",
  },
  {
    category: "gdp",
    fr: "Quel est le PIB de la dernière année disponible ?",
    ar: "ما قيمة الناتج المحلي الإجمالي في آخر سنة متاحة؟",
  },
  {
    category: "gdp",
    fr: "Comment le PIB nominal a-t-il évolué depuis 1998 ?",
    ar: "كيف تطور الناتج المحلي الاسمي منذ 1998؟",
  },
  {
    category: "sectors",
    fr: "Quel est le plus grand secteur économique ?",
    ar: "ما أكبر قطاع اقتصادي؟",
  },
  {
    category: "sectors",
    fr: "Quel secteur est le plus volatil ?",
    ar: "ما القطاع الأكثر تقلباً؟",
  },
  {
    category: "mining",
    fr: "Quelle est la contribution des activités extractives au PIB ?",
    ar: "ما مساهمة الأنشطة الاستخراجية في الناتج؟",
  },
  {
    category: "mining",
    fr: "Comment l’or et le cuivre ont-ils évolué ?",
    ar: "كيف تطور الذهب والنحاس؟",
  },
  {
    category: "trade",
    fr: "Quel est le solde commercial ?",
    ar: "ما الميزان التجاري؟",
  },
  {
    category: "trade",
    fr: "Comparez les exportations et les importations.",
    ar: "قارن بين الصادرات والواردات.",
  },
  {
    category: "comparisons",
    fr: "Comparez la pêche et les activités extractives.",
    ar: "قارن بين الصيد والأنشطة الاستخراجية.",
  },
  {
    category: "comparisons",
    fr: "Comparez la volatilité des principaux secteurs.",
    ar: "قارن تقلب القطاعات الرئيسية.",
  },
  {
    category: "forecasts",
    fr: "Quelle est la prévision du PIB pour les prochaines années ?",
    ar: "ما توقع الناتج المحلي للسنوات القادمة؟",
  },
  {
    category: "forecasts",
    fr: "Quelle méthode de prévision est utilisée ?",
    ar: "ما منهجية التوقع المستخدمة؟",
  },
  {
    category: "scenarios",
    fr: "Que se passerait-il si les activités extractives baissaient de 50 % ?",
    ar: "ماذا يحدث إذا انخفضت الأنشطة الاستخراجية بنسبة 50٪؟",
  },
  {
    category: "scenarios",
    fr: "Proposez un plan de réponse à un choc minier.",
    ar: "اقترح خطة استجابة لصدمة تعدينية.",
  },
  {
    category: "methodology",
    fr: "Quelle est la source des données ?",
    ar: "ما مصدر البيانات؟",
  },
  {
    category: "methodology",
    fr: "Comment les valeurs manquantes sont-elles traitées ?",
    ar: "كيف تعالج القيم المفقودة؟",
  },
];
