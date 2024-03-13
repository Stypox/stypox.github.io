import yaml

# Some invisible project boxes to make sure all project boxes have
# the same size (otherwise with `flex-grow: 1` items on the last
# row may get more stretched if the row is not filled), use a lot
# to make sure this works well even on giant screens.
SECTION_PROJECT_LIST = ("""<div class="section">
    <p class="section_title">{title}</p>
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
        <img class="project_box_image" src="{image}">
        <p class="project_box_title">{title}</p>
        <p class="project_box_description">{description}</p>
    </div>
    <div class="chip_list project_box_chip_list">
        {chips}
    </div>
</div>"""

PROJECT_BOX_LINK = """<a class="project_box_link" href="{link}"></a>"""

CHIP = """<a class="chip chip_{chip_id}" href="#{chip_id}"></a>"""

def read_yaml_file(filename):
    with open(filename, encoding="utf-8") as f:
        return yaml.safe_load(f)

def generate_chips(chip_ids):
    return "\n".join([CHIP.format(chip_id=chip_id) for chip_id in chip_ids])

def generate_project_box(project):
    link = PROJECT_BOX_LINK.format(link=project["link"]) if "link" in project else ""
    if "image" in project:
        return PROJECT_BOX_WITH_IMAGE.format(link=link,
            image="images/" + project["image"], title=project["title"],
            description=project["description"], chips=generate_chips(project["chips"]))
    else:
        return PROJECT_BOX.format(link=link, title=project["title"],
            description=project["description"], chips=generate_chips(project["chips"]))

def generate_object(object_id, obj):
    if obj["type"] == "project":
        return generate_project_box(obj)
    else:
        print("Unknown object type", obj["type"], "for object", object_id)

def generate_projects_section(objects, section):
    items = []
    for object_id in section["items"]:
        obj = objects[object_id]
        items.append(generate_object(object_id, obj))
    return SECTION_PROJECT_LIST.format(title=section["title"],
        items="\n".join(items))

def generate_sections(objects, sections):
    results = []
    for (section_id, section) in sections.items():
        if section["type"] == "projects":
            results.append(generate_projects_section(objects, section))
        else:
            print("Unknown section type", section["type"], "for section", section_id)

    return "\n".join(results)

def main():
    with open("data/template.html", encoding="utf-8") as f:
        template = f.read()
    objects = read_yaml_file("data/objects.yaml")
    content = read_yaml_file("data/content.yaml")

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template.format(home_page_content=generate_sections(objects, content)))

if __name__ == "__main__":
    main()