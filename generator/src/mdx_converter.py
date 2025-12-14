import json
from typing import Callable, Union
from pathlib import Path
from loguru import logger
from src.html_to_mdx import html_to_mdx

def js_escape(text: str) -> str:
    if not text:
        return ""
    return text.replace("\\", "\\\\").replace("'", "\\'").replace('\n', ' ')

def render_details(details: Union[str, list, dict]) -> str:
    if not details:
        return ""
    
    if isinstance(details, str):
        return html_to_mdx(details)
    
    if isinstance(details, list):
        result = []
        for item in details:
            if isinstance(item, dict):
                kind = item.get("kind") or "html"
                content = item.get("content")
                if kind == "html":
                    result.append(html_to_mdx(content))
                elif kind == "example":
                    ex_body = content.get("body", "")
                    result.append(html_to_mdx(ex_body))
            elif isinstance(item, str):
                result.append(html_to_mdx(item))
        return "\n\n".join(result)
        
    return ""

def render_type_table(params: list[dict]) -> str:
    if not params:
        return ""
    
    entries = []
    for param in params:
        name = param["name"]
        
        type_str = " | ".join([t for t in param.get('types', [])])
        
        raw_desc = render_details(param.get('details', '')).strip()
        desc = js_escape(raw_desc)
        
        fields = []
        fields.append(f"      'description': '{desc}'")
        fields.append(f"      'type': '{type_str}'")
        
        if "default" in param:
            def_val = js_escape(str(param["default"]))
            fields.append(f"      'default': '{def_val}'")
            
        fields_str = ",\n".join(fields)
        
        entries.append(f"    '{name}': {{\n{fields_str}\n    }}")
    
    props = ",\n".join(entries)
    return f"""
<TypeTable
  type={{{{
{props}
  }}}}
/>
"""

def render_func(func: dict, heading_level: int = 2) -> str:
    head = "#" * heading_level
    name = func['name']
    path = ".".join(func.get('path', []) + [name])
    
    result = f"\n{head} `{name}`\n\n"
    
    result += render_details(func.get("details", "")) + "\n\n"
    
    params_sig = []
    for p in func.get("params", []):
        p_name = p['name']
        if p.get('named'):
            p_name += ":"
        params_sig.append(p_name)
    
    signature = f"#{path}({', '.join(params_sig)})"
    if 'returns' in func:
        signature += f" -> {' '.join(func['returns'])}"
        
    result += f"```{signature}```\n"

    if func.get("params"):
        result += render_type_table(func["params"]) + "\n"

    if func.get("example"):
        result += "\n**Example:**\n"
        ex = func["example"]
        if isinstance(ex, dict) and "body" in ex:
             result += html_to_mdx(ex["body"]) + "\n"
        else:
             result += render_details(ex) + "\n"

    if func.get("scope"):
        result += f"\n{head}# Definitions\n"
        for scope_func in func["scope"]:
            result += render_func(scope_func, heading_level + 1)

    return result

def get_pages_recursive(json_data: dict, result_list: list, on_item_processed: Callable | None = None) -> None:
    title = json_data.get("title")
    route = json_data.get("route")
    if route:
        route = route.strip("/")

    description = json_data.get("description")
    if description:
        description = description.replace("\n", " ").strip()

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
    details = render_details(category.get("details", ""))
    
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
    result = render_details(symbols.get('details', ''))
    result += "\n\n"
    result += "| Symbol | Name | Math Class |\n"
    result += "| ----- | ----- | ----- |\n"
    for symbol in symbols["list"]:
        value = symbol["value"]
        if value in ["|", "`", "'", '"', "\\", "{", "}", "<", ">"]:
            value = f"\\{value}"
        result += f"| {value} | {symbol['name']} | {symbol['mathClass']} |\n"
    return result

def render_group(group: dict) -> str:
    result = render_details(group.get("details", "")) + "\n\n"
    for func in group.get("functions", []):
        result += render_func(func)
    return result

def render_type(type_data: dict) -> str:
    result = render_details(type_data.get("details", "")) + "\n\n"
    
    if type_data.get("constructor"):
        result += "## Constructor\n"
        result += render_func(type_data["constructor"], heading_level=3)
        
    if type_data.get("scope"):
        result += "\n## Methods\n"
        for method in type_data["scope"]:
            result += render_func(method, heading_level=3)
            
    return result

def render_body(body_type: str, body_content) -> str:
    if body_type == "html":
        return render_details(body_content)
    elif body_type == "category":
        return render_category(body_content)
    elif body_type == "symbols":
        return render_symbols(body_content)
    elif body_type == "func":
        return render_func(body_content)
    elif body_type == "group":
        return render_group(body_content)
    elif body_type == "type":
        return render_type(body_content)
    else:
        logger.warning(f"Skipping unsupported body type: {body_type}")
        return ""

def convert_page_to_mdx(page: dict) -> str:
    title = page.get("title", "Untitled")
    description = (page.get("description") or "").replace('"', '\\"')
    
    body = page.get("body")
    body_content_str = ""
    
    needs_type_table = False
    
    if body:
        body_type = body.get("kind")
        body_data = body.get("content")
        body_content_str = render_body(body_type, body_data)
        
        if "<TypeTable" in body_content_str:
            needs_type_table = True

    imports = ""
    if needs_type_table:
        imports = "import { TypeTable } from 'fumadocs-ui/components/type-table';\n"
    content = f"""---
title: "{title}"
description: "{description}"
---\n{imports}
{body_content_str}
"""
    return content

def generate_mdx_docs(input_json: Path, output_path: Path) -> None:
    json_data = json.loads(input_json.read_text(encoding='utf-8'))

    full_pages_list = []
    for item in json_data:
        get_pages_recursive(item, full_pages_list)
    logger.info(f"Found {len(full_pages_list)} pages")

    for page in full_pages_list:
        logger.info(f"Processing: {page['title']}")
        mdx_content = convert_page_to_mdx(page)
        
        route = page["route"]
        if not route:
            file_path = output_path / "index.mdx"
        elif page["has_children"]:
            folder = output_path / route
            folder.mkdir(parents=True, exist_ok=True)
            file_path = folder / "index.mdx"
        else:
            folder = output_path / route
            folder.parent.mkdir(parents=True, exist_ok=True)
            file_path = Path(str(folder) + ".mdx")
        file_path.write_text(mdx_content, encoding='utf-8')
