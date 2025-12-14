from bs4 import BeautifulSoup, Tag, NavigableString

def html_to_mdx(html_content: str) -> str:
    if not html_content:
        return ""
        
    soup = BeautifulSoup(html_content, "html.parser")
    
    for h1 in soup.find_all("h1"):
        h1.decompose()

    output = []
    
    for element in soup.body.children if soup.body else soup.children:
        res = process_element(element)
        if res:
            output.append(res)

    return "\n\n".join(output)

def process_preview_code(element: Tag) -> str:
    pre_block = element.find("pre")
    if pre_block:
        code_text = pre_block.get_text().strip()
        return f"```typst\n{code_text}\n```"
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
        return text if text else None

    if isinstance(element, Tag):
        classes = element.get("class") or []

        if element.name == "div":
            if "previewed-code" in classes:
                return process_preview_code(element)
            if "info-box" in classes:
                return process_info_box(element)
            return str(element)

        if element.name == "p":
            return "".join([process_inline(child) for child in element.children])

        if element.name in ["h2", "h3", "h4", "h5", "h6"]:
            return process_heading(element)
        
        if element.name == "code" and element.parent.name != "pre":
             return f"`{element.get_text()}`"

        if element.name in ["pre", "table", "ul", "ol", "span"]:
            return str(element)

        if element.name == "details":
            return str(element)
            
        return "".join([process_inline(child) for child in element.children])
        
    return None

def process_inline(element):
    if isinstance(element, NavigableString):
        return str(element).replace("\n", " ")
    
    if isinstance(element, Tag):
        if element.name == "span":
            return str(element)
            
        if element.name == "a":
            href = element.get("href", "")
            text = element.get_text()
            return f"[{text}]({href})"
            
        if element.name in ["strong", "b"]:
            return f"**{element.get_text()}**"
            
        if element.name in ["em", "i"]:
            return f"_{element.get_text()}_"
            
        if element.name == "code":
            return f"`{element.get_text()}`"

        return "".join([process_inline(child) for child in element.children])
        
    return ""
