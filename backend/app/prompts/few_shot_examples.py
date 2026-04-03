"""Few-shot examples for the AI agent — improves accuracy with example Q&A pairs."""

FEW_SHOT_EXAMPLES = [
    {
        "question": "Bu çeyrekte kaç anlaşma kapattık?",
        "answer": {
            "sql": "SELECT COUNT(*) as kapanan_anlaşma FROM deals WHERE stage = 'Closed Won' AND strftime('%Y', close_date) = strftime('%Y', 'now') AND CAST(strftime('%m', close_date) AS INTEGER) BETWEEN (((CAST(strftime('%m', 'now') AS INTEGER) - 1) / 3) * 3 + 1) AND (((CAST(strftime('%m', 'now') AS INTEGER) - 1) / 3) * 3 + 3)",
            "explanation": "Bu çeyrekte 'Closed Won' aşamasındaki anlaşmaları sayıyoruz.",
            "visualization_hint": "number",
            "confidence": 0.9
        }
    },
    {
        "question": "En çok gelir getiren 5 satış temsilcisi kim?",
        "answer": {
            "sql": "SELECT rep_name, SUM(amount) as toplam_gelir, COUNT(*) as anlaşma_sayısı FROM deals WHERE stage = 'Closed Won' GROUP BY rep_name ORDER BY toplam_gelir DESC LIMIT 5",
            "explanation": "Kapanan anlaşmaların toplam tutarına göre en başarılı 5 temsilciyi listeliyoruz.",
            "visualization_hint": "bar_chart",
            "confidence": 0.95
        }
    },
    {
        "question": "Satış hunimiz ne durumda?",
        "answer": {
            "sql": "SELECT stage, COUNT(*) as anlaşma_sayısı, ROUND(SUM(amount), 2) as toplam_tutar, ROUND(AVG(amount), 2) as ortalama_tutar FROM deals WHERE stage NOT IN ('Closed Won', 'Closed Lost') GROUP BY stage ORDER BY CASE stage WHEN 'Prospecting' THEN 1 WHEN 'Qualification' THEN 2 WHEN 'Proposal' THEN 3 WHEN 'Negotiation' THEN 4 END",
            "explanation": "Aktif satış hunisindeki anlaşmaları aşamalarına göre grupladık.",
            "visualization_hint": "table",
            "confidence": 0.95
        }
    },
    {
        "question": "Geçen ay toplam gelirimiz ne kadar oldu?",
        "answer": {
            "sql": "SELECT ROUND(SUM(amount), 2) as toplam_gelir, COUNT(*) as kayıt_sayısı FROM revenue WHERE strftime('%Y-%m', booked_at) = strftime('%Y-%m', 'now', '-1 month')",
            "explanation": "Geçen ayki tüm gelir kayıtlarının toplamını hesaplıyoruz.",
            "visualization_hint": "number",
            "confidence": 0.9
        }
    },
    {
        "question": "Müşterilerimizin sağlık skoru ortalaması nedir?",
        "answer": {
            "sql": "SELECT ROUND(AVG(health_score), 1) as ortalama_skor, MIN(health_score) as en_düşük, MAX(health_score) as en_yüksek, COUNT(*) as müşteri_sayısı FROM customers",
            "explanation": "Tüm müşterilerin sağlık skorlarının istatistiklerini çıkarıyoruz.",
            "visualization_hint": "number",
            "confidence": 0.95
        }
    },
    {
        "question": "Hangi ürün en çok satılıyor?",
        "answer": {
            "sql": "SELECT product, COUNT(*) as satış_sayısı, ROUND(SUM(amount), 2) as toplam_gelir FROM deals WHERE stage = 'Closed Won' GROUP BY product ORDER BY toplam_gelir DESC",
            "explanation": "Kapanan anlaşmalara göre ürünleri gelir sırasına göre listeliyoruz.",
            "visualization_hint": "pie_chart",
            "confidence": 0.95
        }
    },
]


def format_few_shot_for_prompt() -> str:
    """Format few-shot examples as part of the prompt."""
    lines = ["\n## Örnek Soru-Cevaplar\n"]

    for i, example in enumerate(FEW_SHOT_EXAMPLES, 1):
        lines.append(f"### Örnek {i}")
        lines.append(f"**Soru:** {example['question']}")
        lines.append(f"**Yanıt:**")
        lines.append("```json")
        import json
        lines.append(json.dumps(example["answer"], ensure_ascii=False, indent=2))
        lines.append("```\n")

    return "\n".join(lines)
