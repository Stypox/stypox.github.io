import yaml
import os

SECTION_CHIP_LIST = """<p class="header_chip_list_title">{title}</p>
<div class="chip_list header_chip_list">
    {items}
</div>"""

# Some invisible project boxes to make sure all project boxes have
# the same size (otherwise with `flex-grow: 1` items on the last
# row may get more stretched if the row is not filled), use a lot
# to make sure this works well even on giant screens.
SECTION_PROJECT_LIST = ("""<div class="section">
    <p class="section_title" id="{id}">{title}</p>
    <div class="section_project_list">
        {items}""" + """
        <div class="project_box_placeholder"></div>""" * 10 + """
    </div>
</div>""")

PROJECT_BOX = """<div class="project_box">
    {link}
    <p class="project_box_title">{title}</p>
    <p class="project_box_description">{description}</p>
    <div class="chip_list project_box_chip_list">
        {chips}
    </div>
</div>"""

PROJECT_BOX_WITH_IMAGE = """<div class="project_box">
    {link}
    <div class="project_box_image_wrapper">
        {image}
        <p class="project_box_title">{title}</p>
        <p class="project_box_description">{description}</p>
    </div>
    <div class="chip_list project_box_chip_list">
        {chips}
    </div>
</div>"""

PROJECT_BOX_LINK = """<a class="project_box_link" href="{link}"></a>"""

CHIP = """<a class="chip chip_{chip_id}" href="#{chip_id}"></a>"""

HOME_PAGE_TARGET_PAGE = """<div class="home_page_content target_page" id="{id}">
    <div class="toolbar">
        <a class="toolbar_back_button" href="#"></a>
        <p class="toolbar_title">{title}</p>
        {image}
    </div>
    {content}
</div>"""

SECTION_MIXED_LIST = """<div class="section_project_list">
    {items}""" + """
    <div class="project_box_placeholder"></div>""" * 10 + """
</div>"""

def read_yaml_file(filename):
    with open(filename, encoding="utf-8") as f:
        return yaml.safe_load(f)

def format_file(fin, fout, function):
    with open(fin, encoding="utf-8") as f:
        template = f.read()
    with open(fout, "w", encoding="utf-8") as f:
        f.write(function(template))

def pairwise_disjoint(*sets) -> bool:
    union = set().union(*sets)
    return len(union) == sum(map(len, sets))

def extract_image_args(image_args_str):
    image_args = image_args_str.split(" ")
    src = image_args[0]
    if not os.path.exists("images/" + src):
        print("Image does not exist:" + src)
    image_args = image_args[1:]

    try:
        image_args.remove("monochrome")
        monochrome = True
    except ValueError:
        monochrome = False

    scale = None
    if len(image_args) > 1:
        print("Invalid image arguments:", image_args_str)
    elif len(image_args) == 1:
        try:
            scale = float(image_args[0])
        except ValueError:
            print("Invalid scale in image arguments:", image_args_str)

    return src, monochrome, scale

def generate_img(klass, image_args_str):
    src, monochrome, scale = extract_image_args(image_args_str)
    monochrome = " monochrome" if monochrome else ""
    style = "" if scale is None else f"""style="scale: {scale};" """
    return f"""<img class="{klass}{monochrome}" src="images/{src}" {style}/>"""

def generate_img_opt(klass, image_args_str):
    if image_args_str is None:
        return ""
    return generate_img(klass, image_args_str)

def generate_chips_style(chips):
    styles = []
    for (chip_id, chip) in chips.items():
        if "image" in chip:
            src, monochrome, scale = extract_image_args(chip["image"])
            monochrome = " filter: var(--monochrome-filter);" if monochrome else ""
            scale = "" if scale is None else f" transform: scale({scale});"
            styles.append(f""".chip_{chip_id}::before {{ background-image: url("../images/{src}");{monochrome}{scale} }}""")
            styles.append(f""".chip_{chip_id}::after {{ content: "{chip['short']}"; }}""")
        else:
            styles.append(f""".chip_{chip_id}::after {{ padding-left: 0; content: "{chip['short']}"; }}""")
    return "\n" + "\n".join(styles)

def generate_chips(chips, chip_ids):
    results = []
    for chip_id in chip_ids:
        if chip_id in chips:
            results.append(CHIP.format(chip_id=chip_id))
        else:
            print("Unknown chip id", chip_id)
    return "\n".join(results)

def generate_project_box(chips, project, include_hidden_chips):
    link = PROJECT_BOX_LINK.format(link=project["link"]) if "link" in project else ""
    chips_to_show = project["chips"] + project.get("hidden_chips", []) if include_hidden_chips else project["chips"]

    if "image" in project:
        return PROJECT_BOX_WITH_IMAGE.format(link=link,
            image=generate_img("project_box_image", project["image"]), title=project["title"],
            description=project["description"], chips=generate_chips(chips, chips_to_show))
    else:
        return PROJECT_BOX.format(link=link, title=project["title"],
            description=project["description"], chips=generate_chips(chips, chips_to_show))

def generate_object(chips, object_id, obj, include_hidden_chips):
    if obj["type"] == "project":
        return generate_project_box(chips, obj, include_hidden_chips)
    else:
        print("Unknown object type", obj["type"], "for object", object_id)

def generate_chips_section(chips, section):
    return SECTION_CHIP_LIST.format(title=section["title"],
        items=generate_chips(chips, section["items"]))

def generate_projects_section(chips, objects, section_id, section):
    items = []
    for object_id in section["items"]:
        obj = objects[object_id]
        items.append(generate_object(chips, object_id, obj, False))
    return SECTION_PROJECT_LIST.format(id=section_id,
        title=section["title"], items="\n".join(items))

def generate_sections(chips, objects, sections):
    results = []
    for (section_id, section) in sections.items():
        if section["type"] == "projects":
            results.append(generate_projects_section(chips, objects, section_id, section))
        elif section["type"] == "chips":
            results.append(generate_chips_section(chips, section))
        else:
            print("Unknown section type", section["type"], "for section", section_id)

    return "\n".join(results)

def generate_chip_page_content(chips, objects, chip_id):
    items = []
    for (object_id, obj) in objects.items():
        if chip_id in obj["chips"] or chip_id in obj.get("hidden_chips", []):
            items.append(generate_object(chips, object_id, obj, True))
    return SECTION_MIXED_LIST.format(items="\n".join(items))

def generate_home_page_target_pages(chips, objects):
    results = []
    for (chip_id, chip) in chips.items():
        results.append(HOME_PAGE_TARGET_PAGE.format(
            id=chip_id,
            title=chip["title"],
            image=generate_img_opt("toolbar_image", chip.get("image")),
            content=generate_chip_page_content(chips, objects, chip_id)
        ))
    return "\n".join(results)

def main():
    chips = read_yaml_file("data/chips.yaml")
    objects = read_yaml_file("data/objects.yaml")
    header = read_yaml_file("data/header.yaml")
    content = read_yaml_file("data/content.yaml")

    assert pairwise_disjoint(chips, objects, header, content)

    format_file("data/template.html", "index.html", lambda template: template.format(
        home_page_target_pages=generate_home_page_target_pages(chips, objects),
        home_page_header=generate_sections(chips, objects, header),
        home_page_content=generate_sections(chips, objects, content),
    ))

    format_file("styles/style_template.css", "styles/style.css", lambda template: (
        template + generate_chips_style(chips)))

if __name__ == "__main__":
    main()