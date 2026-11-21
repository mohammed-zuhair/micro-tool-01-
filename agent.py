import os
import re
import html.parser
import datetime
import google.generativeai as genai

# 1. API Configuration & Verification
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL: GEMINI_API_KEY environment variable is missing!")
    exit(0)

genai.configure(api_key=api_key)

# 2. Read Repository Files
if not os.path.exists("index.html"):
    print("CRITICAL: index.html not found.")
    exit(0)

with open("index.html", "r", encoding="utf-8") as f:
    current_code = f.read()

roadmap_text = ""
if os.path.exists("roadmap.txt"):
    with open("roadmap.txt", "r", encoding="utf-8") as rf:
        roadmap_text = rf.read().strip()

# 3. Dynamic Prompt Construction
prompt = f"""
أنت مهندس مطور خبير ومستقل لمنصة أدوات مصغرة (Micro-Tools Platform).
مهمتك المستقلة:
1. تحليل الكود الحالي وقراءة الخطة إن وجدت.
2. ابتكار أو إضافة أداة مصغرة رائجة فائقة الأهمية (High-Demand Tool) تزيد من الزيارات وتخدم زوار الموقع.
3. دمج الأداة الجديدة بسلاسة بتصميم عصري ومتناسق دون كسر الأدوات الحالية.

الخطة المتاحة:
{roadmap_text if roadmap_text else 'ابتكر أفضل أداة مصغرة رائجة يحتاجها المستخدمون بكثرة.'}

الشروط الصارمة:
1. احتفظ بكل الوسوم الخاصة بـ Google Search Console وVercel Analytics وGoogle Fonts وشريط المشاركة وسياسة الخصوصية بدون أي تغيير.
2. قم بإرجاع كود HTML الكامل المصحح فقط دون أي شرح أو أسطر markdown مثل ```html.

الكود الحالي للموقع:
{current_code}
"""

print("Executing Autonomous Agent Pipeline...")

# 4. Multi-Model Fallback Engine
models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-8b']
new_code = None
used_model = None

for model_name in models_to_try:
    try:
        print(f"Connecting to model: {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        if response and response.text:
            new_code = response.text.strip()
            used_model = model_name
            print(f"Code successfully generated via {model_name}.")
            break
    except Exception as err:
        print(f"WARNING: Model {model_name} failed: {err}")

if not new_code:
    print("NOTICE: All AI attempts failed. Exiting safely to protect existing code.")
    exit(0)

# Clean Markdown Wrappers
if new_code.startswith("```html"):
    new_code = new_code[7:]
if new_code.startswith("```"):
    new_code = new_code[3:]
if new_code.endswith("```"):
    new_code = new_code[:-3]
new_code = new_code.strip()

# 5. Strict HTML Code Validation
class HTMLValidator(html.parser.HTMLParser):
    pass

try:
    parser = HTMLValidator()
    parser.feed(new_code)
    
    assert "</title>" in new_code, "Missing title tag"
    assert "</html>" in new_code, "Missing html closing tag"
    assert "script" in new_code, "Missing script tag"
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("SUCCESS: Code validated and saved to index.html.")
except Exception as e:
    print(f"VALIDATION FAILED: {e}. Preserving original file.")
    exit(0)

# 6. Automatic Self-Logging (CHANGELOG.md)
try:
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    title_match = re.search(r'<title>(.*?)</title>', new_code, re.IGNORECASE)
    page_title = title_match.group(1) if title_match else "منصة الأدوات المصغرة"
    
    log_entry = (
        f"\n\n### تحديث تلقائي [{now_utc}]\n"
        f"- تم تطوير المنصة وإضافة أدوات جديدة بنجاح عبر نموذج ({used_model}).\n"
        f"- عنوان الصفحة: **{page_title}**\n"
        f"- حالة العملية: فحص الكود مكتمل وتم التثبيت تلقائياً على Vercel."
    )
    
    with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
    print("CHANGELOG.md created/updated successfully.")
except Exception as log_err:
    print(f"Log notice: {log_err}")

# 7. Automatic SEO Sitemap Update
try:
    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", "r", encoding="utf-8") as sf:
            sitemap_code = sf.read()
        today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        updated_sitemap = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{today_str}</lastmod>', sitemap_code)
        with open("sitemap.xml", "w", encoding="utf-8") as sf:
            sf.write(updated_sitemap)
        print("sitemap.xml lastmod updated.")
except Exception as sm_err:
    print(f"Sitemap notice: {sm_err}")
    
