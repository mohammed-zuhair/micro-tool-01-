import os
import re
import html.parser
import datetime
import google.generativeai as genai

# 1. التحقق من مفتاح API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY missing!")
    exit(1)

genai.configure(api_key=api_key)

# 2. التاكد من وجود الملفات الرئيسية
if not os.path.exists("index.html"):
    print("CRITICAL ERROR: index.html not found!")
    exit(1)

with open("index.html", "r", encoding="utf-8") as f:
    current_code = f.read()

roadmap_text = ""
if os.path.exists("roadmap.txt"):
    with open("roadmap.txt", "r", encoding="utf-8") as rf:
        roadmap_text = rf.read().strip()

# 3. الاستكشاف الحي للنماذج المتاحة في الحساب (توصية مجلس النواب لمنع 404)
available_models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    print(f"Discovered active models: {available_models}")
except Exception as e:
    print(f"Model discovery notice: {e}")

if not available_models:
    available_models = [
        'models/gemini-1.5-flash',
        'models/gemini-2.0-flash',
        'models/gemini-1.5-pro'
    ]

# 4. بناء الأمر الحاكم الموحد (Master Prompt)
prompt = f"""
أنت مهندس رئيسي ونظام ذكاء اصطناعي مستقل لتطوير منصات أدوات الويب (Autonomous Full-Stack Agent).

المهمة:
1. تحليل المنصة الحالية وقراءة الدستور.
2. ابتكار وتطوير أداة مصغرة جديدة فائقة الطلب (Viral High-Demand Tool) تتميز بالسرعة والتصميم العصري المظلم المتناسق مع باقي الأدوات.
3. التأكد التام من سلامة كود JavaScript الداخلي وخلوه من أخطاء السينتاكس، وإضافة معالجة الأخطاء (try/catch).
4. الحفاظ الصارم وبدون أي تعديل على وسوم Google Search Console، Vercel Analytics، Google Fonts، شريط المشاركة، وسياسة الخصوصية.

قم بإرجاع المخرجات بالتنسيق المحدد أدناه حصراً دون أي زيادة:

---HTML_START---
[ضع هنا كود HTML الكامل المنقح والمصمم بأسلوب عصري متجاوب، يبتدئ من <!DOCTYPE html> وينتهي بـ </html> فقط دون أسطر markdown]
---HTML_END---

---LOG_START---
[اكتب تقريراً هندسياً باللغة العربية يشرح:
- اسم الأداة الجديدة ومجال استخدامها.
- التحسينات الفنية المعمارية المضافة.
- تقييم الأداء والتجاوب.]
---LOG_END---

الدستور والخطة الحالية:
{roadmap_text}

كود المنصة الحالي:
{current_code}
"""

print("Executing Master Autonomous Engine Pipeline...")

raw_response = None
used_model = None

# 5. محرك التبديل والتنفيذ الذاتي
for model_name in available_models:
    try:
        print(f"Connecting to: {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        if response and response.text:
            raw_response = response.text.strip()
            used_model = model_name
            print(f"Payload successfully generated using {model_name}")
            break
    except Exception as err:
        print(f"WARNING: Model {model_name} failed: {err}")

if not raw_response:
    print("CRITICAL ERROR: Failed to obtain valid payload from active models.")
    exit(1)

# 6. الفصل الهيكلي الصارم بين الكود والتقرير الفني (توصية مجلس الشيوخ)
html_match = re.search(r'---HTML_START---([\s\S]*?)---HTML_END---', raw_response)
log_match = re.search(r'---LOG_START---([\s\S]*?)---LOG_END---', raw_response)

if html_match:
    new_code = html_match.group(1).strip()
else:
    # فلترة احتياطية في حال عدم التزام النموذج بالحدود
    h_match = re.search(r'(<!DOCTYPE\s+html[\s\S]*?</html>|<html[\s\S]*?</html>)', raw_response, re.IGNORECASE)
    new_code = h_match.group(1).strip() if h_match else None

if not new_code or "</html>" not in new_code or "</title>" not in new_code:
    print("CRITICAL ERROR: Generated HTML code is incomplete or malformed.")
    exit(1)

log_details = log_match.group(1).strip() if log_match else "تم تطوير المنصة وإضافة أدوات مصغرة جديدة بنجاح."

# تنظيف أي وسوم markdown متبقية
new_code = re.sub(r'^```html\s*', '', new_code, flags=re.IGNORECASE)
new_code = re.sub(r'^```\s*', '', new_code)
new_code = re.sub(r'\s*```$', '', new_code).strip()

# 7. فحص الجودة والسلامة البنيوية (Strict Code Verification)
class HTMLSyntaxChecker(html.parser.HTMLParser):
    pass

try:
    checker = HTMLSyntaxChecker()
    checker.feed(new_code)
    
    assert "</title>" in new_code, "Validation Failed: Missing <title>"
    assert "</html>" in new_code, "Validation Failed: Missing </html>"
    assert "<script" in new_code, "Validation Failed: Missing <script>"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("SUCCESS: index.html compiled and saved with zero leakages.")
except Exception as val_err:
    print(f"VALIDATION ERROR: {val_err}. Retaining previous stable code.")
    exit(1)

# 8. توثيق السجل الفني (CHANGELOG.md)
try:
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title_match = re.search(r'<title>(.*?)</title>', new_code, re.IGNORECASE)
    page_title = title_match.group(1) if title_match else "منصة الأدوات المصغرة"

    log_entry = (
        f"\n\n## 🏛️ تحديث الصادر عن المجلس الأعلى [{now_utc}]\n"
        f"**المحرك المنفذ:** `{used_model}`\n"
        f"**عنوان المنصة الحالية:** {page_title}\n\n"
        f"### 📋 التقرير الفني والتعديلات:\n"
        f"{log_details}\n"
        f"\n---\n"
    )

    with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
    print("SUCCESS: CHANGELOG.md updated.")
except Exception as log_err:
    print(f"Log writing error: {log_err}")

# 9. تحديث الطابع الزمني لمحركات البحث (sitemap.xml)
if os.path.exists("sitemap.xml"):
    try:
        with open("sitemap.xml", "r", encoding="utf-8") as sf:
            sm_code = sf.read()
        today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        sm_code = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{today_str}</lastmod>', sm_code)
        with open("sitemap.xml", "w", encoding="utf-8") as sf:
            sf.write(sm_code)
        print("SUCCESS: sitemap.xml SEO timestamp updated.")
    except Exception as sm_err:
        print(f"Sitemap update error: {sm_err}")
        
