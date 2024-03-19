import re
import minify_html

def gen_name(i):
    return (chr(ord('A') + i // 52)) + (chr(ord('a') + i % 26) if i % 52 < 26 else chr(ord('A') + i % 26))

with open("index.html", encoding="utf-8") as f:
    html = f.read()
with open("styles/style.css", encoding="utf-8") as f:
    css = f.read()

classes = re.findall(r'class=(?:([^ >"]+)|"([^"]+)")', html)
classes = set(c3 for c1 in classes for c2 in c1 for c3 in c2.split())
try:
    classes.remove("")
except KeyError:
    pass
print(f"Found {len(classes)} unique class names")
classes = sorted(classes, reverse=True)
classes = {name: gen_name(i) for (i, name) in enumerate(classes)}

for old_name, new_name in classes.items():
    css = css.replace(f".{old_name}", f".{new_name}")

def replace_classes(capt):
    capt = capt.group(1) or "" + " " + capt.group(2) or ""
    capt = capt.split()
    capt = [classes[c] for c in capt]
    return "class=\"" + " ".join(capt) + "\""
html = re.sub(r'class=(?:([^ >"]+)|"([^"]+)")', replace_classes, html)

css = minify_html.minify(f"<style>{css}</style>", minify_css=True)[7:-8]
html = minify_html.minify(html,  minify_css=True, do_not_minify_doctype=True)

with open("styles/style.css", "w", encoding="utf-8") as f:
    f.write(css)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
