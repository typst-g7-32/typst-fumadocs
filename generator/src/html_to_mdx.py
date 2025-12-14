import textwrap

from bs4 import BeautifulSoup, Tag, NavigableString
from loguru import logger

def escape_mdx_text(text: str) -> str:
    text = text.replace("\\", "\\\\")

    text = text.replace("&", "\\&")
    text = text.replace("<", "\\<")
    text = text.replace(">", "\\>")

    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")

    text = text.replace("*", "\\*")
    text = text.replace("_", "\\_")
    text = text.replace("`", "\\`")
    return text

def process_footnote_definition(element: Tag) -> str:
    fn_id = element.get("id")
    
    label = element.find(class_="footnote-definition-label")
    if label and isinstance(label, Tag):
        label.decompose()

    content = "".join([process_inline(child) for child in element.children]).strip()
    
    return f"[^{fn_id}]: {content}"

def parse_style_to_jsx(style_str: str) -> str:
    if not style_str:
        return ""
        
    jsx_props = []
    declarations = [d.strip() for d in style_str.split(';') if d.strip()]
    
    for decl in declarations:
        if ':' not in decl:
            continue
            
        prop, val = decl.split(':', 1)
        prop = prop.strip()
        val = val.strip()
        
        if '-' in prop:
            parts = prop.split('-')
            prop = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        
        val = val.replace("'", "\\'")
        
        jsx_props.append(f"{prop}: '{val}'")
        
    return "{{" + ", ".join(jsx_props) + "}}"

def html_to_mdx(html_content: str) -> str:
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    for h1 in soup.find_all("h1"):
        h1.decompose()

    output = []
    
    for element in soup.body.children if soup.body else soup.children:
        result = process_element(element)
        if result:
            output.append(result)

    return "\n\n".join(output)

def process_pre(element: Tag) -> str:
    code_content = element.get_text()
    language = "typst"
    
    return f"```{language}\n{code_content.rstrip()}\n```"

def process_table(element: Tag) -> str:
    rows_md = []
    thead = element.find("thead")
    headers = []
    
    if thead:
        header_row = thead.find("tr")
        if header_row:
            for th in header_row.find_all(["th", "td"]):
                content = "".join([process_inline(child) for child in th.children]).strip().replace("\n", " ")
                headers.append(content)

    if headers:
        rows_md.append("| " + " | ".join(headers) + " |")
        rows_md.append("| " + " | ".join(["---"] * len(headers)) + " |")

    tbody = element.find("tbody")
    tr_source = tbody if tbody else element
    tr_list = tr_source.find_all("tr", recursive=False)

    for tr in tr_list:
        if tr.parent.name == "thead":
            continue

        cells = []
        for td in tr.find_all(["td", "th"]):
             content = "".join([process_inline(child) for child in td.children]).strip().replace("\n", " ")
             cells.append(content)
        
        if cells:
            rows_md.append("| " + " | ".join(cells) + " |")

    return "\n".join(rows_md)


def process_list(element: Tag, depth: int = 0) -> str:
    is_ordered = element.name == "ol"
    items = []
    
    for i, child in enumerate(element.find_all("li", recursive=False)):
        li_content_parts = []
        
        for sub_child in child.children:
            if isinstance(sub_child, Tag) and sub_child.name in ["ul", "ol"]:
                nested_list = process_list(sub_child, depth + 1)
                li_content_parts.append("\n" + nested_list)
            else:
                processed = process_inline(sub_child)
                if processed:
                    li_content_parts.append(processed)
        
        content = "".join(li_content_parts).strip()
        
        indent = "  " * depth
        marker = f"{i+1}. " if is_ordered else "- "
        
        items.append(f"{indent}{marker}{content}")

    return "\n".join(items)

def process_preview_code(element: Tag) -> str:
    pre_block = element.find("pre")
    image_block = element.find("img")
    if not pre_block:
        return ""
    code_text = pre_block.get_text().rstrip()
    if not image_block:
        return f"```typst\n{code_text}\n```"
    if image_block and pre_block:
        if not isinstance(image_block, Tag):
            logger.warning(f"Skipping unsupported image block: {image_block}")
            return ""
        src = image_block.get('src', "")
        alt = image_block.get('alt', "")
        code_text = code_text.replace("`", "\\`")
        code_text = textwrap.indent(code_text, "  ")
        code_text = "{" + f"`\n{code_text}\n`" + "}"
        return f"<TypstPreview\n  code={code_text}\n  image='{src}'\n  alt='{alt}'\n  editable={{true}}\n/>"
    return ""

def process_info_box(element: Tag) -> str:
    children_processed = [process_element(child) for child in element.children]
    inner_content = "\n\n".join(filter(None, children_processed))
    return f"<Callout>\n{inner_content}\n</Callout>"

def process_heading(element: Tag) -> str:
    level = int(element.name[1])
    text = element.get_text(strip=True)
    return f"{'#' * level} {text}"

def process_element(element):
    if isinstance(element, NavigableString):
        text = str(element).strip()
        return escape_mdx_text(text) if text else None

    if isinstance(element, Tag):
        classes = element.get("class") or []

        if element.name == "div":
            if "previewed-code" in classes:
                return process_preview_code(element)
            if "info-box" in classes:
                return process_info_box(element)
            if "footnote-definition" in classes:
                return process_footnote_definition(element)
            
            children_md = "".join([process_inline(child) for child in element.children])
            
            attrs = ""
            if classes:
                attrs += f' className="{" ".join(classes)}"'
            
            style = element.get("style")
            if style:
                jsx_style = parse_style_to_jsx(style)
                attrs += f' style={jsx_style}'

            return f"<div{attrs}>\n{children_md}\n</div>"
        
        if element.name == "a":
            href = element.get("href", "")
            if isinstance(href, list):
                href = "".join([process_inline(child) for child in href])
            if href.startswith("/"):
                href = "/docs" + href
            text = "".join([process_inline(child) for child in element.children]).strip()
            return f"[{text}]({href})"

        if element.name == "p":
            return "".join([process_inline(child) for child in element.children])

        if element.name in ["h2", "h3", "h4", "h5", "h6"]:
            return process_heading(element)
        
        if element.name == "code" and element.parent.name != "pre":
            language = "typst"
            text = element.get_text().rstrip()
            return f'`{text}{{:{language}}}`'

        if element.name == "pre":
            return process_pre(element)
        
        if element.name == "table":
            return process_table(element)
        
        if element.name == "span":
            return str(element)

        if element.name == "details":
            return str(element)
        
        if element.name in ["ul", "ol"]:
            return process_list(element)
            
        return "".join([process_inline(child) for child in element.children])
    
    return None

def process_inline(element):
    if isinstance(element, NavigableString):
        return escape_mdx_text(str(element).replace("\n", " "))
    
    if isinstance(element, Tag):
        if element.name == "img":
            src = element.get("src", "")
            alt = element.get("alt", "")
            style = element.get("style")
            
            attrs = f'src="{src}" alt="{alt}"'
            
            if style:
                jsx_style = parse_style_to_jsx(style)
                attrs += f' style={jsx_style}'
            
            if element.get("width"): attrs += f' width="{element.get("width")}"'
            if element.get("height"): attrs += f' height="{element.get("height")}"'

            return f"<img {attrs} />"
        
        if element.name == "span":
            return str(element)
            
        if element.name == "a":
            href = element.get("href", "")
            if isinstance(href, list):
                href = "".join([process_inline(child) for child in href])
            if href.startswith("/"):
                href = "/docs" + href
            text = "".join([process_inline(child) for child in element.children]).strip()
            return f"[{text}]({href})"
            
        if element.name in ["strong", "b"]:
            return f"**{element.get_text()}**"
            
        if element.name in ["em", "i"]:
            return f"_{element.get_text()}_"
            
        if element.name == "code":
            language = "typst"
            text = element.get_text().strip()
            text = text.replace("{", "\\{").replace("}", "\\}")
            if text == "`":
                return "```"
            return f'`{text}{{:{language}}}`'

        return "".join([process_inline(child) for child in element.children])
        
    return ""
