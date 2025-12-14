import json
from typing import Callable
from pathlib import Path

from loguru import logger

from src.html_to_mdx import html_to_mdx

def count_pages(json_data: dict) -> int:
    count = 1
    for child in json_data.get("children", []):
        count += count_pages(child)
    return count

def get_pages_recursive(json_data: dict, result_list: list, on_item_processed: Callable | None = None) -> None:
    title = json_data.get("title")

    route = json_data.get("route")
    if route:
        route = route.strip("/")

    description = json_data.get("description")
    if description:
        description = description.replace("\n", "").strip()

    part = json_data.get("part")
    body = json_data.get("body")
    has_children = bool(json_data.get("children"))
    
    result_list.append({
        "title": title,
        "route": route,
        "description": description,
        "part": part,
        "body": body,
        "has_children": has_children
    })

    if on_item_processed:
        on_item_processed(title)

    for children in json_data.get("children", []):
        get_pages_recursive(children, result_list, on_item_processed)

def render_category(category: dict) -> str:
    details = html_to_mdx(category["details"])

    rows = "\n".join(
        f'    <tr>\n'
        f'      <td width="20px" align="center">—</td>\n'
        f'      <td><code><a href="{item["route"]}">{item["name"]}</a></code></td>\n'
        f'      <td>{item["oneliner"]}</td>\n'
        f'    </tr>'
        for item in category["items"]
    )

    table = f"""
<table>
  <thead>
    <tr>
      <th width="20px"></th>
      <th align="left">Name</th>
      <th align="left">Description</th>
    </tr>
  </thead>
  <tbody>
{rows}
  </tbody>
</table>
""".strip()
    return f"{details}\n\n## Definitions\n\n{table}\n"

def render_symbols(symbols: dict) -> str:
    # TODO: Improve this
    result = html_to_mdx(symbols['details'])
    result += "\n\n"

    result += "| Symbol | Name | Math Class |\n"
    result += "| ----- | ----- | ----- |\n"
    for symbol in symbols["list"]:
        value = symbol["value"]
        if value in ["|", "`", "'", '"', "\\"]:
            value = f"\\{value}"
        result += f"| {value} | {symbol['name']} | {symbol['mathClass']} |\n"

    return result

def render_group(group: dict) -> str:
    result = html_to_mdx(group["details"])
    for func in group["functions"]:
        result += render_func(func)
    return result

def render_body(body_type: str, body_content) -> str:
    if body_type == "html":
        return html_to_mdx(body_content)
    elif body_type == "category":
        return render_category(body_content)
    elif body_type == "symbols":
        return render_symbols(body_content)
    else:
        print(f"{body_type} is currently not supported")
        return f"{body_type} is currently not supported"

def convert_page_to_mdx(page: dict) -> str:
    title = page.get("title")
    description = page.get("description")
    body = page.get("body")
    if body:
        body_type = body.get("kind")
        body_content = body.get("content")
        body = render_body(body_type, body_content)
    
    content = f"""\
---
title: {title}
description: {description}
---
{body}
"""
    return content

def generate_mdx_docs(input_json: Path, output_path: Path) -> None:
    json_data = json.loads(input_json.read_text())

    full_pages_list = []
    
    for item in json_data:
        get_pages_recursive(item, full_pages_list)
    logger.info(f"Found {len(full_pages_list)} pages")

    for page in full_pages_list:
        print(page["title"], page["route"])
        mdx_content = convert_page_to_mdx(page)
        if page["route"] == "":
            output_path.joinpath("index.mdx").write_text(mdx_content)
            continue
        if page["has_children"]:
            output_path.joinpath(page["route"]).mkdir(parents=True, exist_ok=True)
            output_path.joinpath(page["route"], "index.mdx").write_text(mdx_content)
            continue
        output_path.joinpath(page["route"] + ".mdx").write_text(mdx_content)