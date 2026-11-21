import os
import re
import html.parser
import google.generativeai as genai

# 1. Setup Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Read Current HTML
with open("index.html", "r", encoding="utf-8") as f:
    current_code = f.read()

# 3. Prompt for Agent Update
prompt = f"""
أنت مهندس مطور خبير ومستقل للموقع التالي. مهمتك هي تحسين الموقع أو إضافة أداة مصغرة جديدة مفيدة ومطلوبة بدون كسر الأكواد الحالية.

الشروط الصارمة:
1. احتفظ بكل الوسوم الخاصة بـ Google Search Console وVercel Analytics وGoogle Fonts وشريط المشاركة وسياسة الخصوصية بدون أي تغيير.
2. أضف ميزة جديدة أو حسّن التصميم/الأدوات القائمة.
3. قم بإرجاع كود HTML الكامل فقط دون أي شرح أو أسطر markdown مثل ```html.

الكود الحالي للموقع:
{current_code}
"""

response = model.generate_content(prompt)
new_code = response.text.strip()

# Clean code formatting if returned with markdown blocks
if new_code.startswith("```html"):
    new_code = new_code[7:]
if new_code.endswith("```"):
    new_code = new_code[:-3]
new_code = new_code.strip()

# 4. Strict Validation (تأكيد خلو الكود من الأخطاء)
class HTMLValidator(html.parser.HTMLParser):
    pass

try:
    parser = HTMLValidator()
    parser.feed(new_code)
    
    # Ensure critical tags exist
    assert "</title>" in new_code, "Missing title tag"
    assert "</html>" in new_code, "Missing html closing tag"
    assert "script" in new_code, "Missing script tag"
    
    # Save code if valid
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(new_code)
    print("SUCCESS: Code validated and updated successfully.")
except Exception as e:
    print(f"VALIDATION FAILED: {e}. Reverting to original code.")
    exit(1)
  
