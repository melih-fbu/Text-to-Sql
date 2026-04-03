"""AI Agent — Text-to-SQL with Google Gemini (with demo fallback)."""

import json
import re
from typing import Optional

from app.config import settings
from app.prompts.system_prompt import get_system_prompt, get_interpretation_prompt
from app.prompts.few_shot_examples import format_few_shot_for_prompt
from app.services.schema_discovery import discover_sqlite_schema, format_schema_for_prompt
from app.services.guardrails import validate_sql
from app.services.query_executor import execute_sqlite_query, QueryResult


# ─── Demo Mode Keyword Mappings ───────────────────────────
# When no Gemini API key is set, these patterns handle common questions.
DEMO_QUERIES = [
    {
        "keywords": ["kaç anlaşma", "anlaşma sayısı", "deal count", "toplam anlaşma"],
        "sql": "SELECT stage, COUNT(*) as anlaşma_sayısı, ROUND(SUM(amount), 2) as toplam_tutar FROM deals GROUP BY stage ORDER BY anlaşma_sayısı DESC",
        "explanation": "Anlaşmaları aşamalarına göre grupladık.",
        "hint": "table",
    },
    {
        "keywords": ["satış huni", "pipeline", "funnel", "huni durumu"],
        "sql": "SELECT stage, COUNT(*) as anlaşma_sayısı, ROUND(SUM(amount), 2) as toplam_tutar, ROUND(AVG(amount), 2) as ortalama_tutar FROM deals WHERE stage NOT IN ('Closed Won', 'Closed Lost') GROUP BY stage ORDER BY CASE stage WHEN 'Prospecting' THEN 1 WHEN 'Qualification' THEN 2 WHEN 'Proposal' THEN 3 WHEN 'Negotiation' THEN 4 END",
        "explanation": "Aktif satış hunisindeki anlaşmaları aşamalarına göre grupladık.",
        "hint": "table",
    },
    {
        "keywords": ["en çok gelir", "en başarılı", "top temsilci", "en iyi satıcı", "top rep", "5 temsilci"],
        "sql": "SELECT rep_name as temsilci, COUNT(*) as kapanan_anlaşma, ROUND(SUM(amount), 2) as toplam_gelir FROM deals WHERE stage = 'Closed Won' GROUP BY rep_name ORDER BY toplam_gelir DESC LIMIT 5",
        "explanation": "Kapanan anlaşmaların toplam tutarına göre en başarılı 5 temsilciyi listeliyoruz.",
        "hint": "bar_chart",
    },
    {
        "keywords": ["toplam gelir", "total revenue", "gelir ne kadar", "revenue"],
        "sql": "SELECT ROUND(SUM(amount), 2) as toplam_gelir, COUNT(*) as kayıt_sayısı, ROUND(AVG(amount), 2) as ortalama FROM revenue WHERE year = 2026",
        "explanation": "2026 yılındaki toplam geliri hesaplıyoruz.",
        "hint": "number",
    },
    {
        "keywords": ["müşteri sağlık", "health score", "sağlık skoru"],
        "sql": "SELECT ROUND(AVG(health_score), 1) as ortalama_skor, MIN(health_score) as en_düşük, MAX(health_score) as en_yüksek, COUNT(*) as müşteri_sayısı FROM customers",
        "explanation": "Tüm müşterilerin sağlık skorlarının istatistiklerini çıkarıyoruz.",
        "hint": "number",
    },
    {
        "keywords": ["ürün", "product", "en çok satıl", "hangi ürün"],
        "sql": "SELECT product as ürün, COUNT(*) as satış_sayısı, ROUND(SUM(amount), 2) as toplam_gelir FROM deals WHERE stage = 'Closed Won' GROUP BY product ORDER BY toplam_gelir DESC",
        "explanation": "Kapanan anlaşmalara göre ürünleri gelir sırasında listeliyoruz.",
        "hint": "pie_chart",
    },
    {
        "keywords": ["bölge", "region", "bölgelere göre"],
        "sql": "SELECT region as bölge, COUNT(*) as anlaşma_sayısı, ROUND(SUM(amount), 2) as toplam_tutar FROM deals GROUP BY region ORDER BY toplam_tutar DESC",
        "explanation": "Bölgelere göre anlaşma ve gelir dağılımını gösteriyoruz.",
        "hint": "bar_chart",
    },
    {
        "keywords": ["ortalama satış", "satış döngüsü", "sales cycle", "kaç gün"],
        "sql": "SELECT rep_name as temsilci, ROUND(AVG(avg_sales_cycle_days), 1) as ort_satış_süresi_gün, ROUND(AVG(quota_attainment), 1) as kota_yüzdesi FROM team_performance GROUP BY rep_name ORDER BY ort_satış_süresi_gün",
        "explanation": "Temsilcilere göre ortalama satış döngüsü sürelerini hesapladık.",
        "hint": "table",
    },
    {
        "keywords": ["kapanan", "closed won", "kapattık", "kapatılan"],
        "sql": "SELECT rep_name as temsilci, COUNT(*) as kapanan_anlaşma, ROUND(SUM(amount), 2) as toplam_tutar, ROUND(AVG(amount), 2) as ortalama_tutar FROM deals WHERE stage = 'Closed Won' GROUP BY rep_name ORDER BY toplam_tutar DESC",
        "explanation": "Kapanan (Closed Won) anlaşmaları temsilcilere göre listeledik.",
        "hint": "table",
    },
    {
        "keywords": ["kota", "quota", "hedef", "performans"],
        "sql": "SELECT rep_name as temsilci, quarter as çeyrek, ROUND(quota, 2) as kota, ROUND(revenue_generated, 2) as gelir, ROUND(quota_attainment, 1) as başarı_yüzdesi FROM team_performance WHERE year = 2026 ORDER BY başarı_yüzdesi DESC",
        "explanation": "2026 yılı temsilci kota performanslarını gösteriyoruz.",
        "hint": "table",
    },
]


def _match_demo_query(question: str) -> Optional[dict]:
    """Try to match a question to a demo query using keywords."""
    q_lower = question.lower()
    best_match = None
    best_score = 0

    for dq in DEMO_QUERIES:
        score = sum(1 for kw in dq["keywords"] if kw.lower() in q_lower)
        if score > best_score:
            best_score = score
            best_match = dq

    return best_match if best_score > 0 else None


class BruinAgent:
    """AI-powered Text-to-SQL agent using Google Gemini (with demo fallback)."""

    def __init__(self):
        self._use_gemini = False
        self.model = None
        self._schema_cache: Optional[dict] = None
        self._schema_text: Optional[str] = None

        if settings.gemini_api_key and settings.gemini_api_key != "demo-key":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                self._use_gemini = True
                print("🧠 Gemini AI bağlantısı kuruldu")
            except Exception as e:
                print(f"⚠️ Gemini bağlanamadı: {e}. Demo modda çalışıyor.")
        else:
            print("🎮 Demo modda çalışıyor (Gemini API key ayarlanmamış)")

    async def _get_schema(self, db_path: str) -> str:
        """Get formatted schema text, with caching."""
        if self._schema_text is None:
            schema = await discover_sqlite_schema(db_path)
            self._schema_cache = schema
            self._schema_text = format_schema_for_prompt(schema)
        return self._schema_text

    def invalidate_schema_cache(self):
        """Force re-discovery of schema on next query."""
        self._schema_cache = None
        self._schema_text = None

    async def question_to_sql(self, question: str, db_path: str) -> dict:
        """
        Convert a natural language question to SQL.

        Returns:
            {
                "sql": "SELECT ...",
                "explanation": "...",
                "visualization_hint": "table|number|...",
                "confidence": 0.95
            }
        """
        # Demo mode: use keyword matching
        if not self._use_gemini:
            match = _match_demo_query(question)
            if match:
                return {
                    "sql": match["sql"],
                    "explanation": match["explanation"],
                    "visualization_hint": match["hint"],
                    "confidence": 0.85,
                }
            else:
                # Default fallback: show all tables summary
                return {
                    "sql": "SELECT 'deals' as tablo, COUNT(*) as kayıt_sayısı FROM deals UNION ALL SELECT 'customers', COUNT(*) FROM customers UNION ALL SELECT 'revenue', COUNT(*) FROM revenue UNION ALL SELECT 'activities', COUNT(*) FROM activities UNION ALL SELECT 'team_performance', COUNT(*) FROM team_performance",
                    "explanation": "Sorunuz tanınamadı. İşte veritabanındaki tabloların özeti. İpucu: 'satış hunisi', 'toplam gelir', 'en çok gelir getiren temsilci' gibi sorular sorun.",
                    "visualization_hint": "table",
                    "confidence": 0.3,
                }

        # Gemini mode: use AI
        schema_text = await self._get_schema(db_path)
        few_shots = format_few_shot_for_prompt()

        system_prompt = get_system_prompt(schema_text)
        full_prompt = f"{system_prompt}\n{few_shots}\n\n## Kullanıcı Sorusu\n{question}"

        try:
            import google.generativeai as genai
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                ),
            )

            response_text = response.text.strip()
            parsed = self._parse_agent_response(response_text)
            return parsed

        except Exception as e:
            # Fallback to demo mode on Gemini error
            match = _match_demo_query(question)
            if match:
                return {
                    "sql": match["sql"],
                    "explanation": f"⚠️ AI hatası, demo modda yanıt: {match['explanation']}",
                    "visualization_hint": match["hint"],
                    "confidence": 0.7,
                }
            return {
                "sql": None,
                "explanation": f"Üzgünüm, sorunuzu anlayamadım: {str(e)}",
                "visualization_hint": "text",
                "confidence": 0.0,
                "error": str(e),
            }

    async def interpret_results(
        self, question: str, sql: str, result: QueryResult
    ) -> str:
        """Generate a human-friendly interpretation of query results."""
        # Prepare result summary
        if result.row_count == 0:
            return "🔍 Sorgunuz için herhangi bir sonuç bulunamadı."

        # Format sample data for the prompt
        sample_data = result.to_table_data()[:20]  # Max 20 rows for context
        result_text = json.dumps(sample_data, ensure_ascii=False, indent=2, default=str)

        interpretation_prompt = get_interpretation_prompt()
        prompt = f"""{interpretation_prompt}

## Kullanıcının Sorusu
{question}

## Çalıştırılan SQL
{sql}

## Sorgu Sonuçları ({result.row_count} satır, {result.execution_time_ms}ms)
{result_text}

## Yanıtın (Türkçe):"""

        try:
            import google.generativeai as genai
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=1024,
                ),
            )
            return response.text.strip()
        except Exception as e:
            return f"Sonuçlar alındı ({result.row_count} satır) ancak yorumlama sırasında hata oluştu."

    async def ask(self, question: str, db_path: str) -> dict:
        """
        Full pipeline: Question → SQL → Execute → Interpret.

        Returns the complete response dict.
        """
        # Step 1: Generate SQL
        agent_response = await self.question_to_sql(question, db_path)

        if not agent_response.get("sql"):
            return {
                "success": False,
                "question": question,
                "error": agent_response.get("explanation", "SQL üretilemedi."),
                "sql": None,
                "result": None,
                "interpretation": agent_response.get("explanation"),
            }

        sql = agent_response["sql"]

        # Step 2: Validate SQL
        is_safe, sanitized_sql, error_msg = validate_sql(sql, settings.max_query_rows)
        if not is_safe:
            return {
                "success": False,
                "question": question,
                "error": error_msg,
                "sql": sql,
                "result": None,
                "interpretation": error_msg,
            }

        # Step 3: Execute
        try:
            result = execute_sqlite_query(db_path, sanitized_sql, settings.max_query_rows)
        except Exception as e:
            return {
                "success": False,
                "question": question,
                "error": str(e),
                "sql": sanitized_sql,
                "result": None,
                "interpretation": f"❌ Sorgu çalıştırılırken hata oluştu: {str(e)}",
            }

        # Step 4: Interpret
        interpretation = await self.interpret_results(question, sanitized_sql, result)

        return {
            "success": True,
            "question": question,
            "sql": sanitized_sql,
            "explanation": agent_response.get("explanation", ""),
            "visualization_hint": agent_response.get("visualization_hint", "table"),
            "confidence": agent_response.get("confidence", 0.0),
            "result": result.to_dict(),
            "interpretation": interpretation,
            "execution_time_ms": result.execution_time_ms,
        }

    def _parse_agent_response(self, text: str) -> dict:
        """Parse the AI agent's JSON response, handling various formats."""
        # Try to find JSON in the response
        # Pattern 1: ```json ... ```
        json_match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Pattern 2: { ... } anywhere in the text
        json_match = re.search(r"\{[^{}]*\"sql\"[^{}]*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Pattern 3: Try the entire text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Pattern 4: Extract SQL directly if JSON parsing fails
        sql_match = re.search(r"(?:SELECT|WITH)\s+.*?(?:;|\Z)", text, re.DOTALL | re.IGNORECASE)
        if sql_match:
            return {
                "sql": sql_match.group(0).strip().rstrip(";"),
                "explanation": "AI yanıtı JSON formatında değildi, SQL doğrudan çıkarıldı.",
                "visualization_hint": "table",
                "confidence": 0.6,
            }

        return {
            "sql": None,
            "explanation": f"AI yanıtından SQL çıkarılamadı. Ham yanıt: {text[:200]}",
            "visualization_hint": "text",
            "confidence": 0.0,
        }


# Singleton agent instance
agent = BruinAgent()
