import os
import re
import sys
import datetime
import google.generativeai as genai

# 1. API Verification
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY is missing!")
    sys.exit(1)

genai.configure(api_key=api_key)

TOOLS_DIR = "tools"
os.makedirs(TOOLS_DIR, exist_ok=True)

# 2. Cleanup Function for Corrupted Files in tools/
def cleanup_corrupted_tools():
    if not os.path.exists(TOOLS_DIR):
        return
    for fname in os.listdir(TOOLS_DIR):
        fpath = os.path.join(TOOLS_DIR, fname)
        if os.path.isfile(fpath):
            name_no_ext = fname.replace(".html", "").strip(".-_")
            if fname == ".html" or fname.startswith("-") or len(name_no_ext) < 2:
                try:
                    os.remove(fpath)
                    print(f"CLEANUP: Removed corrupted file -> {fname}")
                except Exception as e:
                    print(f"Cleanup notice: {e}")

# 3. Filename Sanitizer Engine
def sanitize_filename(raw_name, fallback_title):
    clean = raw_name.lower().strip()
    clean = re.sub(r'```[a-z]*', '', clean)
    for ch in ['"', "'", '`']:
        clean = clean.replace(ch, '')
    clean = re.sub(r'\b(text|html|code|markdown|filename)\b', '', clean)
    clean = clean.replace(' ', '-')
    clean = re.sub(r'[^a-z0-9\-_]', '', clean)
    clean = clean.strip('.-_')
    
    if not clean or len(clean) < 3:
        clean = re.sub(r'[^a-z0-9]', '', fallback_title.lower())
        if len(clean) < 3:
            clean = f"tool-{int(datetime.datetime.now().timestamp())}"
            
    return f"{clean}.html"

# 4. Smart Model Discovery
def get_active_text_models():
    candidate_models = []
    try:
        for m in genai.list_models():
            name = m.name.lower()
            if any(skip in name for skip in ['tts', 'audio', 'lyria', 'image', 'transcribe', 'robotics', 'computer-use', 'antigravity']):
                continue
            if 'generateContent' in m.supported_generation_methods:
                candidate_models.append(m.name)
    except Exception as e:
        print(f"Model discovery notice: {e}")
    
    priority_models = [
        'models/gemini-2.0-flash',
        'models/gemini-1.5-flash',
        'models/gemini-1.5-pro',
        'models/gemini-flash-latest'
    ]
    
    final_list = [m for m in priority_models if m in candidate_models]
    for m in candidate_models:
        if m not in final_list:
            final_list.append(m)
            
    return final_list if final_list else priority_models

# 5. Targeted Generation
def generate_incremental_update(roadmap_text):
    existing_tools = os.listdir(TOOLS_DIR) if os.path.exists(TOOLS_DIR) else []
    models = get_active_text_models()
    
    prompt = f"""
أنت مهندس مطور أنظمة ويب (Surgical Incremental Code Architect).
مهمتك:
1. ابتكار أداة مصغرة جديدة فائقة الطلب (Viral High-Demand Tool).
2. توليد صفحة HTML مستقلة خفيفة جداً لهذه الأداة ليتم حفظها في مجلد tools/.
3. ضرورة إدراج رابط العودة للصفحة الرئيسية (<a href="../index.html">العودة للرئيسية</a>) في أعلى الأداة.
4. توليد قصاصة الكرت (Card Snippet) المخصص لهذه الأداة فقط ليتم حُقنه في الصفحة الرئيسية دون إعادة كتابة index.html.

الأدوات الحالية لمنع التكرار: {existing_tools}
الخطة/الدستور: {roadmap_text}

أخرج المخرجات بالتنسيق الصارم التالي حصراً:

---FILENAME---
[اسم الملف بالإنجليزية فقط بحروف وشحطات مثل: unit-converter.html]
---TITLE---
[اسم الأداة بالعربية]
---DESC---
[وصف الأداة في سطر واحد]
---TOOL_HTML_START---
[ضع كود صفحة الأداة المستقلة الكامل هنا من <!DOCTYPE html> إلى </html>]
---TOOL_HTML_END---

---CARD_SNIPPET_START---
[ضع كود HTML الخاص ببطاقة الأداة فقط لإضافتها في index.html مثل: <a href="tools/filename.html" class="tool-card">...</a>]
---CARD_SNIPPET_END---

---LOG_START---
[تقرير فني مختصر عن الأداة]
---LOG_END---
"""

    gen_config = genai.GenerationConfig(max_output_tokens=4096, temperature=0.2)

    for model_name in models:
        try:
            print(f"Generating surgical update via {model_name}...")
            model = genai.GenerativeModel(model_name, generation_config=gen_config)
            res = model.generate_content(prompt, request_options={"timeout": 180})
            
            if res and res.text:
                text = res.text.strip()
                file_match = re.search(r'---FILENAME---([\s\S]*?)---TITLE---', text)
                title_match = re.search(r'---TITLE---([\s\S]*?)---DESC---', text)
                desc_match = re.search(r'---DESC---([\s\S]*?)---TOOL_HTML_START---', text)
                tool_html_match = re.search(r'---TOOL_HTML_START---([\s\S]*?)---TOOL_HTML_END---', text)
                card_match = re.search(r'---CARD_SNIPPET_START---([\s\S]*?)---CARD_SNIPPET_END---', text)
                log_match = re.search(r'---LOG_START---([\s\S]*?)---LOG_END---', text)
                
                if file_match and tool_html_match and card_match:
                    raw_fname = file_match.group(1).strip()
                    title = title_match.group(1).strip() if title_match else "أداة مصغرة"
                    desc = desc_match.group(1).strip() if desc_match else "أداة جديدة"
                    
                    filename = sanitize_filename(raw_fname, title)

