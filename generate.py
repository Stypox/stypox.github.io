import yaml
import os


HOME_PAGE_TARGET_PAGE = """<div class="home_page_content target_page" id="{id}">
    <div class="toolbar">
        <a class="toolbar_home_button" href="#"></a>
        {image}
        <p class="toolbar_title">{title}</p>
    </div>
    {content}
</div>"""


CHIP = """<a class="chip chip_{chip_id}" href="#{chip_id}"></a>"""

CHIP_LIST = """<div class="chip_list {additional_classes}">
    {chips}
</div>"""

HEADER_CHIP_LIST = """<p class="header_chip_list_title">{title}</p>
<div class="chip_list header_chip_list">
    {items}
</div>"""


# Some invisible project boxes to make sure all project boxes have
# the same size (otherwise with `flex-grow: 1` items on the last
# row may get more stretched if the row is not filled), use a lot
# to make sure this works well even on giant screens.
SECTION_TITLE_LIST = ("""<div class="section">
    <p class="{title_class}" id="{id}">{title}</p>
    <div class="section_box_list {list_class}">
        {items}""" + """
        <div class="box_placeholder"></div>""" * 10 + """
    </div>
</div>""")

SECTION_MIXED_LIST = """<div class="section_box_list {list_class}">
    {items}""" + """
    <div class="box_placeholder"></div>""" * 10 + """
</div>"""


PROJECT_BOX = """<div class="box project_box">
    {link}
    <div>
        {image}
        <p class="box_title {title_class}">{title}</p>
        <p class="project_box_description">{description}</p>
    </div>
    {chips}
</div>"""

CATEGORY_BOX = """<div class="box category_box">
    {link}
    {image}
    <p class="{title_class}">{title}</p>
</div>"""
ALL_PROJECTS_BOX = """<a href="#all-projects" class="box category_box category_box_all_projects">All projects</a>"""
OR_CLICK_ON_CHIPS_BOX = f"""<div class="category_box category_box_or_click_on_chips">Or click on chips, e.g. {CHIP.format(chip_id='rust')}</div>"""

JOB_BOX = """<div class="box">
    {link}
    <div>
        <span class="box_title job_box_title">{title}</span>
        {company}
        {when}
    </div>
    {image}
    <p class="job_box_description">{description}</p>
    {chips}
</div>"""

COMPETITION_BOX = """<div class="box competition_box">
    {link}
    <p class="box_title competition_box_title {ellipsize_class}">{title}</p>
    <p class="competition_box_description {ellipsize_class}">{description}</p>
    {chips}
</div>"""

TALK_BOX = """<div class="box talk_box">
    {link}
    <p class="box_title talk_box_title {ellipsize_class}">{title}</p>
    <p class="talk_box_description {ellipsize_class}">{description}</p>
    {chips}
</div>"""

ALL_COMPETITIONS_TALKS_BOX = """<div class="box_list_all_competitions_talks">
    <a href="#all-competitions" class="box_all_competitions_talks">All competitions</a>
    <a href="#all-talks" class="box_all_competitions_talks">All talks</a>
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

def format_opt(format_string, format_arg, alt=""):
    if format_arg is None:
        return alt
    return format_string % format_arg

def join_opt(*items, sep=" • "):
    items = [
        str(item)
        for item in items
        if item is not None and not len(str(item)) == 0
    ]
    return sep.join(items)

def generate_img(klass, image_args_str):
    src, monochrome, scale = extract_image_args(image_args_str)
    monochrome = " monochrome" if monochrome else ""
    style = "" if scale is None else f"""style="scale: {scale};" """
    return f"""<img class="{klass}{monochrome}" src="images/{src}" {style}/>"""

def generate_img_opt(klass, image_args_str, alt=""):
    if image_args_str is None:
        return alt
    return generate_img(klass, image_args_str)

def generate_link(link):
    return f"""<a class="box_overlaid_link" href="{link}"></a>"""

def generate_link_opt(link, alt=""):
    if link is None:
        return alt
    return generate_link(link)

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

def generate_chip_list_for_obj(chips, obj, expanded_form, list_class):
    chips_to_show = obj["chips"] + obj.get("hidden_chips", []) if expanded_form else obj["chips"]
    additional_class = "" if expanded_form else "chip_list_single_line"
    return CHIP_LIST.format(
        chips=generate_chips(chips, chips_to_show),
        additional_classes=additional_class + " " + list_class,
    )

def generate_project_box(chips, project, expanded_form, title_class):
    return PROJECT_BOX.format(
        link=generate_link_opt(project.get("link")),
        image=generate_img_opt("project_box_image", project.get("image")),
        title_class=title_class,
        title=project["title"],
        description=project["description"],
        chips=generate_chip_list_for_obj(chips, project, expanded_form, "project_box_chip_list"),
    )

def generate_job_box(chips, job, expanded_form):
    return JOB_BOX.format(
        link=generate_link_opt(job.get("link")),
        image=generate_img_opt("job_box_image", job.get("image")),
        title=job["title"],
        company=f"""• <span class="job_box_company">{job['company']}</span>""" if "company" in job else "",
        when=f"""• <span class="job_box_when">{job['when']}</span>""" if "when" in job else "",
        description=job["description"],
        chips=generate_chip_list_for_obj(chips, job, expanded_form, "job_box_chip_list"),
    )

def generate_competition_box(chips, competition, expanded_form):
    return COMPETITION_BOX.format(
        link=generate_link_opt(competition.get("link")),
        title=join_opt(competition.get("place", ""), competition['title']),
        description=join_opt(competition.get("date"), competition.get("description")),
        ellipsize_class="" if expanded_form else "ellipsize",
        chips=generate_chip_list_for_obj(chips, competition, expanded_form, "competition_box_chip_list"),
    )

def generate_talk_box(chips, talk, expanded_form):
    return TALK_BOX.format(
        link=generate_link_opt(talk.get("link")),
        title=talk['title'],
        description=join_opt(talk.get("date"), talk.get("description")),
        ellipsize_class="" if expanded_form else "ellipsize",
        chips=generate_chip_list_for_obj(chips, talk, expanded_form, "talk_box_chip_list"),
    )

def generate_object(chips, object_id, obj, expanded_form):
    if obj["type"] == "project":
        return generate_project_box(chips, obj, expanded_form, "project_box_normal_title")
    elif obj["type"] == "project-contributed":
        return generate_project_box(chips, obj, expanded_form, "project_box_contributed_title")
    elif obj["type"] == "project-work":
        return generate_project_box(chips, obj, expanded_form, "project_box_work_title")
    elif obj["type"] == "job":
        return generate_job_box(chips, obj, expanded_form)
    elif obj["type"] == "competition":
        return generate_competition_box(chips, obj, expanded_form)
    elif obj["type"] == "talk":
        return generate_talk_box(chips, obj, expanded_form)
    else:
        print("Unknown object type", obj["type"], "for object", object_id)
        return ""

def generate_category_box(chips, chip_id):
    if chip_id == "all-projects":
        return ALL_PROJECTS_BOX
    elif chip_id == "or-click-on-chips":
        return OR_CLICK_ON_CHIPS_BOX
    else:
        return CATEGORY_BOX.format(
            image=generate_img_opt("category_box_image", chips[chip_id].get("image")),
            link=generate_link(f"#{chip_id}"),
            title_class="category_box_title",
            title=chips[chip_id]["title"],
        )

def generate_chips_section(chips, section):
    return HEADER_CHIP_LIST.format(title=section["title"],
        items=generate_chips(chips, section["items"]))

def generate_projects_section(chips, objects, section, **format_kwargs):
    items = []
    for object_id in section["items"]:
        obj = objects[object_id]
        items.append(generate_object(chips, object_id, obj, False))
    return SECTION_TITLE_LIST.format(list_class="section_project_list",
        items="\n".join(items), **format_kwargs)

def generate_categories_section(chips, section, **format_kwargs):
    items = []
    for chip_id in section["items"]:
        items.append(generate_category_box(chips, chip_id))
    return SECTION_TITLE_LIST.format(list_class="section_category_list",
        items="\n".join(items), **format_kwargs)

def generate_jobs_section(chips, objects, section, **format_kwargs):
    items = []
    for object_id in section["items"]:
        obj = objects[object_id]
        items.append(generate_object(chips, object_id, obj, False))
    return SECTION_TITLE_LIST.format(list_class="section_job_list",
        items="\n".join(items), **format_kwargs)

def generate_competitions_section(chips, objects, section, **format_kwargs):
    items = []
    for object_id in section["items"]:
        if object_id == "all-competitions-talks":
            items.append(ALL_COMPETITIONS_TALKS_BOX)
            continue
        obj = objects[object_id]
        items.append(generate_object(chips, object_id, obj, False))
    return SECTION_TITLE_LIST.format(list_class="section_competition_list",
        items="\n".join(items), **format_kwargs)

def generate_talks_section(chips, objects, section, **format_kwargs):
    items = []
    for object_id in section["items"]:
        if object_id == "all-competitions-talks":
            items.append(ALL_COMPETITIONS_TALKS_BOX)
            continue
        obj = objects[object_id]
        items.append(generate_object(chips, object_id, obj, False))
    return SECTION_TITLE_LIST.format(list_class="section_talk_list",
        items="\n".join(items), **format_kwargs)

def generate_sections(chips, objects, sections):
    results = []
    for (section_id, section) in sections.items():
        if section["type"] == "chips":
            results.append(generate_chips_section(chips, section))
            continue

        format_kwargs = {
            "id": section_id,
            "title_class": "section_subtitle" if section.get("subtitle", False) else "section_title",
            "title": section["title"],
        }
        if section["type"] == "projects":
            results.append(generate_projects_section(chips, objects, section, **format_kwargs))
        elif section["type"] == "categories":
            results.append(generate_categories_section(chips, section, **format_kwargs))
        elif section["type"] == "jobs":
            results.append(generate_jobs_section(chips, objects, section, **format_kwargs))
        elif section["type"] == "competitions":
            results.append(generate_competitions_section(chips, objects, section, **format_kwargs))
        elif section["type"] == "talks":
            results.append(generate_talks_section(chips, objects, section, **format_kwargs))
        else:
            print("Unknown section type", section["type"], "for section", section_id)

    return "\n".join(results)

def generate_chip_page_content(chips, objects, chip_id):
    items = []
    for (object_id, obj) in objects.items():
        if chip_id in obj["chips"] or chip_id in obj.get("hidden_chips", []):
            items.append(generate_object(chips, object_id, obj, True))
    return SECTION_MIXED_LIST.format(list_class="section_project_list", items="\n".join(items))

def generate_all_page_content(chips, objects, list_class, types):
    items = []
    for (object_id, obj) in objects.items():
        if obj["type"] in types:
            items.append(generate_object(chips, object_id, obj, True))
    return SECTION_MIXED_LIST.format(list_class=list_class, items="\n".join(items))

def generate_home_page_target_pages(chips, objects):
    results = []

    # a target page for each chip
    for (chip_id, chip) in chips.items():
        results.append(HOME_PAGE_TARGET_PAGE.format(
            id=chip_id,
            title=chip["title"],
            image=generate_img_opt("toolbar_image", chip.get("image"),
                alt="""<div class="toolbar_image"></div>"""),
            content=generate_chip_page_content(chips, objects, chip_id),
        ))

    # a target page for each object type
    for (page_id, title, list_class, types) in (
        ("all-projects", "projects", "section_project_list", ("project", "project-contributed", "project-work")),
        ("all-jobs", "jobs", "section_job_list", ("job")),
        ("all-competitions", "competitions", "section_competition_list", ("competition")),
        ("all-talks", "talks", "section_talk_list", ("talk")),
    ):
        results.append(HOME_PAGE_TARGET_PAGE.format(
            id=page_id,
            title=f"All {title}, sorted chronologically",
            image="""<div class="toolbar_image"></div>""",
            content=generate_all_page_content(chips, objects, list_class, types),
        ))

    return "\n".join(results)

def main():
    chips = read_yaml_file("data/chips.yaml")
    objects = read_yaml_file("data/objects.yaml")
    header = read_yaml_file("data/header.yaml")
    content = read_yaml_file("data/content.yaml")
    used_keywords = ["all-projects", "all-competitions-talks", "or-click-on-chips"]

    assert pairwise_disjoint(chips, objects, header, content, used_keywords)

    format_file("data/template.html", "index.html", lambda template: template.format(
        home_page_target_pages=generate_home_page_target_pages(chips, objects),
        home_page_header=generate_sections(chips, objects, header),
        home_page_content=generate_sections(chips, objects, content),
    ))

    format_file("data/template.css", "styles/style.css", lambda template: (
        template + generate_chips_style(chips)))

if __name__ == "__main__":
    main()