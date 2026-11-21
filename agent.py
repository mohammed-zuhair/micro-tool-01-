import os
import re
import sys
import ast
import html.parser
import datetime
import google.generativeai as genai

# ==============================================================================
# 1. إعداد المفتاح والتحقق الأول لبيئة التنفيذ
# ==============================================================================
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY is missing!")
    sys.exit(1)

genai.configure(api_key=api_key)

# ==============================================================================
# 2. محرك الفلترة الذكي وتصفية النماذج النصية المستقرة
# ==============================================================================
def get_active_text_models():
    candidate_models = []
    try:
        for m in genai.list_models():
            name = m.name.lower()
            # استثناء النماذج غير النصية (الصوت، الصور، الموسيقى، الروبوتات)
            if any(skip in name for skip in ['tts', 'audio', 'lyria', 'image', 'transcribe', 'robotics', 'computer-use', 'antigravity']):
                continue
            if 'generateContent' in m.supported_generation_methods:
                candidate_models.append(m.name)
    except Exception as e:
        print(f"Model listing notice: {e}")
    
    priority_models = [
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-flash-latest',
        'models/gemini-pro-latest'
    ]
    
    final_list = [m for m in priority_models if m in candidate_models]
    for m in candidate_models:
        if m not in final_list:
            final_list.append(m)
            
    return final_list if final_list else priority_models

# ==============================================================================
# 3. محرك البناء والمراجعة المزدوج (مجلس النواب + مجلس الشيوخ)
# ==============================================================================
def run_dual_council_pipeline(current_html, roadmap):
    models = get_active_text_models()
    
    master_prompt = f"""
أنت تعمل كنظام ذكاء اصطناعي مزدوج (مجلس النواب للمشروعات والابتكار + مجلس الشيوخ للمراجعة والحصانة البرمجية).

[دور مجلس النواب - الابتكار]:
1. قراءة الدستور وتحديد أداة مصغرة جديدة رائجة ومطلوبة بكثرة (Viral Tool).
2. كتابة كود الأداة بلغة JavaScript عصرية، متجاوبة، وسريعة، مع معالجة الأخطاء (try/catch).

[دور مجلس الشيوخ - التدقيق الصارم]:
1. التأكد من تطابق الهوية البصرية وخلو الكود من أخطاء Syntax.
2. الحفاظ الصارم على وسوم Google Search Console, Vercel Analytics, Google Fonts, Privacy Policy وشريط المشاركة.
3. التأكد من فصل كود الـ HTML عن التقرير الفني نهائياً.

صيغة المخرجات المطلوبة حصراً:
---HTML_START---
[ضع كود HTML الكامل المنقح يبتدئ من <!DOCTYPE html> وينتهي بـ </html> فقط]
---HTML_END---

---LOG_START---
[تقرير مفصل باللغة العربية يشرح اسم الأداة، فوائدها الفنية، وقرار المجلسين]
---LOG_END---

الدستور والخطة:
{roadmap}

الكود الحالي:
{current_html}
"""
    
    for model_name in models:
        try:
            print(f"Council engaging model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(master_prompt, request_options={"timeout": 300})
            if response and response.text:
                text = response.text.strip()
                if "</html>" in text and ("<!DOCTYPE" in text or "<html" in text):
                    return text, model_name
        except Exception as err:
            print(f"Warning: Model {model_name} failed in council pipeline: {err}")
            
    return None, None

# ==============================================================================
# 4. محرك الاستشفاء وتعديل السكريبت الذاتي (Self-Healing Routine)
# ==============================================================================
def attempt_self_healing(error_message):
    print("\n⚠️ ACTIVATING SELF-HEALING ENGINE: Modifying agent.py autonomously...")
    
    if not os.path.exists("agent.py"):
        return False
        
    with open("agent.py", "r", encoding="utf-8") as f:
        self_code = f.read()
        
    models = get_active_text_models()
    healing_prompt = f"""
حدث خطأ غير متوقع أثناء تنفيذ سكريبت البايثون (agent.py).
مهمتك كـ "مهندس معالجة الأخطاء الذاتية":
1. تحليل رسالة الخطأ وكود agent.py الحالي.
2. إعادة كتابة وتعديل كود agent.py لتصحيح هذا الخطأ وضمان استقرار التشغيل.
3. قم بإرجاع كود البايثون الجديد المصحح فقط بدون أي شرح أو وسوم markdown مثل ```python.

رسالة الخطأ:
{error_message}

كود agent.py الحالي:
{self_code}
"""
    
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(healing_prompt, request_options={"timeout": 300})
            if res and res.text:
                new_py_code = res.text.strip()
                new_py_code = re.sub(r'^```python\s*', '', new_py_code, flags=re.IGNORECASE)
                new_py_code = re.sub(r'^```\s*', '', new_py_code)
                new_py_code = re.sub(r'\s*```$', '', new_py_code).strip()
                
                # فحص السلامة البنيوية لكود البايثون لمنع تعطيل المحرك (Syntax Verification)
                ast.parse(new_py_code)
                
                with open("agent.py", "w", encoding="utf-8") as f:
                    f.write(new_py_code)
                    
                print(f"SUCCESS: agent.py autonomously self-healed and updated via {model_name}.")
                
                # تسجيل العملية في السجل
                now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
                    log_file.write(f"\n\n### 🛡️ عملية استشفاء وتطوير ذاتي [{now_utc}]\n- قام الإيجنت بتشخيص خطأ التشغيل وأصلح كود `agent.py` بنفسه تلقائياً.\n- الخطأ المعالج: `{error_message[:150]}...`\n---\n")
                return True
        except SyntaxError as syn_err:
            print(f"Self-healing syntax error in generated code: {syn_err}")
        except Exception as heal_err:
            print(f"Self-healing model attempt failed: {heal_err}")
            
    return False

# ==============================================================================
# 5. نقطة الدخول والتنفيذ الرئيسية (Main Execution Block)
# ==============================================================================
if __name__ == "__main__":
    try:
        if not os.path.exists("index.html"):
            raise FileNotFoundError("index.html file missing")
            
        with open("index.html", "r", encoding="utf-8") as f:
            current_code = f.read()
            
        roadmap_text = ""
        if os.path.exists("roadmap.txt"):
            with open("roadmap.txt", "r", encoding="utf-8") as rf:
                roadmap_text = rf.read().strip()
                
        print("Starting Autonomous Agent Council Pipeline...")
        raw_response, used_model = run_dual_council_pipeline(current_code, roadmap_text)
        
        if not raw_response:
            raise RuntimeError("All models failed to return a valid HTML payload.")
            
        # استخلاص الكود والتقرير
        html_match = re.search(r'---HTML_START---([\s\S]*?)---HTML_END---', raw_response)
        log_match = re.search(r'---LOG_START---([\s\S]*?)---LOG_END---', raw_response)
        
        if html_match:
            new_code = html_match.group(1).strip()
        else:
            h_match = re.search(r'(<!DOCTYPE\s+html[\s\S]*?</html>|<html[\s\S]*?</html>)', raw_response, re.IGNORECASE)
            new_code = h_match.group(1).strip() if h_match else None
            
        if not new_code or "</html>" not in new_code:
            raise ValueError("Extracted HTML is broken or incomplete.")
            
        log_details = log_match.group(1).strip() if log_match else "تم تطوير المنصة وإضافة ميزات جديدة بنجاح."
        
        # تنظيف الأكواد
        new_code = re.sub(r'^```html\s*', '', new_code, flags=re.IGNORECASE)
        new_code = re.sub(r'^```\s*', '', new_code)
        new_code = re.sub(r'\s*```$', '', new_code).strip()
        
        # فحص HTML
        class HTMLValidator(html.parser.HTMLParser):
            pass
        validator = HTMLValidator()
        validator.feed(new_code)
        
        assert "</title>" in new_code and "</html>" in new_code and "<script" in new_code
        
        # حفظ الملفات
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_code)
        print("SUCCESS: index.html updated successfully.")
        
        # كتابة السجل
        now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        title_match = re.search(r'<title>(.*?)</title>', new_code, re.IGNORECASE)
        page_title = title_match.group(1) if title_match else "منصة الأدوات المصغرة"
        
        log_entry = (
            f"\n\n## 🏛️ قرار المجلس الأعلى للتطوير [{now_utc}]\n"
            f"**النموذج المنفذ:** `{used_model}`\n"
            f"**عنوان المنصة:** {page_title}\n\n"
            f"### 📋 التقرير الفني والتعديلات:\n"
            f"{log_details}\n"
            f"\n---\n"
        )
        with open("CHANGELOG.md", "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
        print("SUCCESS: CHANGELOG.md updated.")
        
        # تحديث sitemap
        if os.path.exists("sitemap.xml"):
            with open("sitemap.xml", "r", encoding="utf-8") as sf:
                sm_code = sf.read()
            today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
            sm_code = re.sub(r'<lastmod>.*?</lastmod>', f'<lastmod>{today_str}</lastmod>', sm_code)
            with open("sitemap.xml", "w", encoding="utf-8") as sf:
                sf.write(sm_code)
            print("SUCCESS: sitemap.xml updated.")

    except Exception as main_exception:
        err_msg = str(main_exception)
        print(f"\n❌ PIPELINE ERROR DETECTED: {err_msg}")
        healed = attempt_self_healing(err_msg)
        if healed:
            print("Self-healing finished. The updated script will run on the next cycle.")
            sys.exit(0) # خروج آمن يسمح بـ Commit للتعديل الذاتي
        else:
            print("CRITICAL: Self-healing failed.")
            sys.exit(1)
                  
