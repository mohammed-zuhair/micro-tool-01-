import os
import re
import html.parser
import datetime
import google.generativeai as genai

# 1. API Configuration
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY missing!")
    exit(1)

genai.configure(api_key=api_key)

# 2. Read Repository Files
if not os.path.exists("index.html"):
    print("ERROR: index.html not found!")
    exit(1)

with open("index.html", "r", encoding="utf-8") as f:
    current_code = f.read()

roadmap_text = ""
if os.path.exists("roadmap.txt"):
    with open("roadmap.txt", "r", encoding="utf-8") as rf:
        roadmap_text = rf.read().strip()

# 3. Dynamic Prompt Construction
prompt = f"""
أنت مهندس مطور خبير ومستقل لمنصة أدوات مصغرة (Micro-Tools Platform).
مهمتك:
1. تحليل الكود الحالي وقراءة الخطة.
2. إضافة أداة مصغرة جديدة ورائجة ومفيدة كلياً بتصميم متناسق وسلس.
3. احتفظ بكل الوسوم الخاصة بـ Google Search Console وVercel Analytics وGoogle Fonts وشريط المشاركة وسياسة الخصوصية بدون أي تغيير.
4. قم بإرجاع كود HTML الكامل فقط دون أي أسطر markdown مثل ```html.

الخطة:
{roadmap_text}

الكود الحالي:
{current_code}
"""

print("Executing AI Code Generation...")

# 4. Multi-Model Execution
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
            text = response.text.strip()
            text = re.sub(r'^```html\s*', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            text = text.strip()
            
            if "</html>" in text and "</title>" in text:
                new_code = text
                used_model = model_name
                print(f"SUCCESS: Generated valid code via {model_name}")
                break
    except Exception as err:
        print(f"WARNING: Model {model_name} failed: {err}")

if not new_code:
    print("CRITICAL ERROR: Failed to generate valid code from all models.")
    exit(1)

# 5. Save HTML Changes
with open("index.html", "w", encoding="utf-8") as f:
    f.write(new_code)
print("SUCCESS: index.html updated.")

# 6. Force Write CHANGELOG.md
now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
title_match = re.search(r'<title>(.*?)</title>', new_code, re.IGNORECASE)
page_title = title_match.group(1) if title_match else "منصة الأدوات المصغرة"

log_entry = (
    f"\n\n### تحديث جديد [{now_utc}]\n"
    f"- تم إضافة أدوات جديدة وتحديث المنصة بنجاح عبر ({used_model}).\n"
    f"- عنوان الصفحة: **{page_title}**"
)

with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
    log_file.write(log_entry)
print("SUCCESS: CHANGELOG.md updated.")

# 7. Update Sitemap
if os.path.exists("sitemap.xml"):
    try:
        with open("sitemap.xml", "r", encoding="utf-8") as sf:
            sm_code = sf.read()
        today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        sm_code = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{today_str}</lastmod>', sm_code)
        with open("sitemap.xml", "w", encoding="utf-8") as sf:
            sf.write(sm_code)
        print("SUCCESS: sitemap.xml updated.")
    except Exception as sm_err:
        print(f"Sitemap error: {sm_err}")
        
