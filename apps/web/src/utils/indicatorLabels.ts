const labels:Record<string,{fr:string;ar:string}>={
 gdp_activity_market_prices:{fr:'PIB aux prix du marché selon les activités',ar:'الناتج المحلي الإجمالي بأسعار السوق حسب الأنشطة'},
 primary_sector:{fr:'Secteur primaire',ar:'القطاع الأولي'},secondary_sector:{fr:'Secteur secondaire',ar:'القطاع الثانوي'},tertiary_sector:{fr:'Secteur tertiaire',ar:'القطاع الثالثي'},
 extractive_activities:{fr:'Activités extractives',ar:'الأنشطة الاستخراجية'},construction_public_works:{fr:'Bâtiment et travaux publics',ar:'البناء والأشغال العامة'},
 snim_iron:{fr:'Fer (SNIM)',ar:'الحديد (سنيم)'},gold_copper:{fr:'Or et cuivre',ar:'الذهب والنحاس'},oil_gas_extraction:{fr:'Pétrole et gaz',ar:'النفط والغاز'},
 manufacturing:{fr:'Industrie manufacturière',ar:'الصناعة التحويلية'},commerce:{fr:'Commerce',ar:'التجارة'},agriculture_forestry:{fr:'Agriculture et sylviculture',ar:'الزراعة والغابات'},fishing:{fr:'Pêche',ar:'الصيد البحري'},
}
export function indicatorLabel(code:string,language:'fr'|'ar'){return labels[code]?.[language]??(language==='ar'?'مؤشر غير مسمى':'Indicateur non libellé')}
