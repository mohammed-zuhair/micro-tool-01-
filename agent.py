import os
import re
import html.parser
import google.generativeai as genai

# 1. Verify GEMINI_API_KEY
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY environment variable is missing!")
    exit(1)

genai.configure(api_key=api_key)

# 2. Read Current HTML Code
with open("index.html", "r", encoding="utf-8") as f:
    current_code = f.read()

# 3. Dynamic Prompt for Auto-Discovering Trending Tools
prompt = f"""
أنت مهندس مطور خبير وخبير SEO لأدوات الويب المصغرة (Viral & Trending Micro-Tools).
مهمتك:
1. تحليل الكود الحالي للموقع والأدوات الموجودة فيه.
2. اكتشاف وبناء أداة مصغرة جديدة (High-Demand Tool) تكون رائدة ومطلوبة بكثرة من الزوار (مثل: أدوات تحويل البيانات، حاسبات سريعة، مولدات نصوص/رموز، أدوات SEO مصغرة، أو أدوات المطورين).
3. دمج الأداة الجديدة بسلاسة بتصميم عصري ومتناسق دون كسر الأدوات الحالية.

الشروط الصارمة:
1. احتفظ بكل الوسوم الخاصة بـ Google Search Console وVercel Analytics وGoogle Fonts وشريط المشاركة وسياسة الخصوصية بدون أي تغيير.
2. قم بإرجاع كود HTML الكامل فقط دون أي شرح أو أسطر markdown مثل ```html.

الكود الحالي للموقع:
{current_code}
"""

print("Searching trending tool ideas and executing code generation pipeline...")

# 4. Multi-Model Fallback Strategy
models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-8b']
new_code = None

for model_name in models_to_try:
    try:
        print(f"Attempting API request with model: {model_name}...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        if response and response.text:
            new_code = response.text.strip()
            print(f"SUCCESS: Generated updated code using {model_name}.")
            break
    except Exception as err:
        print(f"WARNING: Model {model_name} failed with error: {err}")

if not new_code:
    print("NOTICE: All AI model attempts failed or rate limited. Safe exit.")
    exit(0)

# Clean Markdown Wrapper formatting
if new_code.startswith("```html"):
    new_code = new_code[7:]
if new_code.startswith("```"):
    new_code = new_code[3:]
if new_code.endswith("```"):
    new_code = new_code[:-3]
new_code = new_code.strip()

# 5. Strict HTML Code Validation Stage
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
    print("SUCCESS: Code validated and written to index.html.")
except Exception as e:
    print(f"VALIDATION FAILED: {e}. Reverting changes.")
    exit(1)

# 6. Automated Changelog & Summary Generator
try:
    summary_prompt = "في سطرين فقط باللغة العربية، اكتب ملخصاً مشوقاً للأداة الجديدة أو التحسين الذي أضفته للموقع الآن."
    model_sum = genai.GenerativeModel('gemini-1.5-flash')
    sum_res = model_sum.generate_content(summary_prompt)
    log_text = sum_res.text.strip() if sum_res else "تم إضافة أداة مصغرة جديدة وتحديث البنية."
    
    with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
        log_file.write(f"\n\n### تحديث جديد:\n- {log_text}")
    print(f"CHANGELOG UPDATED: {log_text}")
except Exception as log_err:
    print(f"Log generation notice: {log_err}")
    
