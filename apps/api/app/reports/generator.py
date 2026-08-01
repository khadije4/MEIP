from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path

from app.analytics.anomalies import detect_anomalies
from app.analytics.forecasting import InsufficientObservationsError, generate_forecast
from app.analytics.growth import annual_growth_series, summarize


def generate_csv(name: str, series: dict[int, float], unit: str, source: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(["indicator", name]); writer.writerow(["source", source]); writer.writerow(["unit", unit])
    writer.writerow(["year", "value", "nominal_growth_pct"])
    growth = annual_growth_series(series)
    for year in sorted(series): writer.writerow([year, series[year], growth.get(year) if growth.get(year) is not None else "NA"])
    return stream.getvalue().encode("utf-8-sig")


def _rtl(text: str) -> str:
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(text))


def generate_pdf(name: str, series: dict[int, float], unit: str, source: str, language: str, source_side: str, include_forecast: bool) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    out = io.BytesIO(); styles = getSampleStyleSheet(); font = "Helvetica"
    if language == "ar":
        for path in (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/tahoma.ttf")):
            if path.exists(): pdfmetrics.registerFont(TTFont("MEIPArabic", str(path))); font = "MEIPArabic"; break
    def tx(fr: str, ar: str) -> str: return _rtl(ar) if language == "ar" else fr
    body = ParagraphStyle("MEIPBody", parent=styles["BodyText"], fontName=font, alignment=2 if language == "ar" else 0, leading=15)
    title = ParagraphStyle("MEIPTitle", parent=styles["Title"], fontName=font, textColor=colors.HexColor("#006233"), alignment=2 if language == "ar" else 1)
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    years = sorted(series); summary = summarize(series); growth = annual_growth_series(series); alerts = detect_anomalies(series)
    story = [Paragraph(tx("Rapport économique MEIP", "تقرير منصة الذكاء الاقتصادي الموريتاني"), title), Spacer(1, 8),
        Paragraph(tx(f"Indicateur : {name}", f"المؤشر: {name}"), body),
        Paragraph(tx(f"Période : {years[0]}–{years[-1]}", f"الفترة: {years[0]}–{years[-1]}"), body),
        Paragraph(tx(f"Source : {source} | Unité : {unit}", f"المصدر: {source} | الوحدة: {unit}"), body),
        Paragraph(tx("Attention : valeurs nominales à prix courants; elles ne mesurent pas la croissance réelle.", "تنبيه: القيم اسمية بالأسعار الجارية ولا تقيس النمو الحقيقي."), body), Spacer(1, 8),
        Paragraph(tx(f"Résumé : dernière valeur {summary.latest_value:,.2f} en {summary.latest_year}; minimum {summary.min_value:,.2f} en {summary.min_year}; maximum {summary.max_value:,.2f} en {summary.max_year}.", f"الملخص: أحدث قيمة {summary.latest_value:,.2f} سنة {summary.latest_year}؛ أدنى قيمة {summary.min_value:,.2f} سنة {summary.min_year}؛ أعلى قيمة {summary.max_value:,.2f} سنة {summary.max_year}."), body)]
    rows = [[tx("Année", "السنة"), tx("Valeur", "القيمة"), tx("Croissance nominale %", "النمو الاسمي ٪")]]
    for y in years: rows.append([str(y), f"{series[y]:,.2f}", "NA" if growth[y] is None else f"{growth[y]:.2f}"])
    table = Table(rows, repeatRows=1, colWidths=[35*mm, 55*mm, 55*mm]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#006233")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,-1),font),("GRID",(0,0),(-1,-1),0.3,colors.grey),("ALIGN",(0,0),(-1,-1),"RIGHT" if language=="ar" else "LEFT")]))
    story += [Spacer(1,8), table, Spacer(1,8), Paragraph(tx(f"Anomalies détectées : {len(alerts)} (MAD et score Z robuste).", f"الشذوذ المكتشف: {len(alerts)} (الانحراف المطلق الوسيط ودرجة Z المتينة)."), body)]
    if include_forecast:
        try:
            fc = generate_forecast(series)
            forecast_text = ", ".join(f"{y}: {v:,.2f}" for y,v in zip(fc.horizon_years, fc.predicted_values))
            story.append(Paragraph(tx(f"Prévision expérimentale ({fc.model_name}, fiabilité {fc.reliability}) : {forecast_text}. Non officielle.", f"توقع تجريبي ({fc.model_name}، الموثوقية {fc.reliability}): {forecast_text}. غير رسمي."), body))
        except InsufficientObservationsError:
            story.append(Paragraph(tx("Prévision indisponible : moins de huit observations.", "التوقع غير متاح: أقل من ثماني مشاهدات."), body))
    story += [Paragraph(tx("Méthode : observations importées, croissance annuelle consécutive, statistiques descriptives et détection robuste. Les valeurs manquantes ne sont pas remplacées par zéro.", "المنهجية: مشاهدات مستوردة، نمو سنوي متتال، إحصاءات وصفية وكشف متين. لا تستبدل القيم المفقودة بصفر."), body), Paragraph(tx(f"Généré le {datetime.now(timezone.utc).date().isoformat()}.", f"تاريخ الإنشاء: {datetime.now(timezone.utc).date().isoformat()}."), body)]
    doc.build(story); return out.getvalue()
