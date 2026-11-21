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

# 3. Prompt Construction
prompt = f"""
أنت مهندس مطور خبير ومستقل للموقع التالي. مهمتك هي تحسين الموقع أو إضافة أداة مصغرة جديدة مفيدة ومطلوبة بدون كسر الأكواد الحالية.

الشروط الصارمة:
1. احتفظ بكل الوسوم الخاصة بـ Google Search Console وVercel Analytics وGoogle Fonts وشريط المشاركة وسياسة الخصوصية بدون أي تغيير.
2. أضف ميزة جديدة أو حسّن التصميم/الأدوات القائمة.
3. قم بإرجاع كود HTML الكامل فقط دون أي شرح أو أسطر markdown مثل ```html.

الكود الحالي للموقع:
{current_code}
"""

print("Executing AI Agent code generation pipeline...")

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
        exit(0)
        

# Prevent breaking the workflow if API limit is reached
if not new_code:
    print("NOTICE: All AI model attempts failed or rate limited. Safe exit to protect existing site.")
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
    
    # Ensure mandatory website tags are strictly present
    assert "</title>" in new_code, "Missing title tag"
    assert "</html>" in new_code, "Missing html closing tag"
    assert "script" in new_code, "Missing script tag"
    
    # Write verified code to index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("SUCCESS: Code validated and written to index.html.")
except Exception as e:
    print(f"VALIDATION FAILED: {e}. Reverting changes to preserve stability.")
    exit(1)
    
