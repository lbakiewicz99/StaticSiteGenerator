from textnode import TextType, TextNode, BlockType
from htmlnode import LeafNode, HTMLNode, ParentNode
import re
import os
import shutil

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            if not text_node.url:
                raise ValueError("LINK requires url")
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            if not text_node.url:
                raise ValueError("IMAGE requires url")
            return LeafNode("img","",{"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Unknown TextType: {text_node.text_type}")
        
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    #print(old_nodes)
    text_list = []
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            text_list = node.text.split(delimiter)
            if len(text_list) % 2 == 0:
                raise Exception("Invalid markdown syntax")
            for i in range(len(text_list)):
                if i % 2 == 0:
                    new_nodes.append(TextNode(text_list[i],TextType.TEXT))
                if i % 2 == 1:
                    new_nodes.append(TextNode(text_list[i],text_type))
    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def split_nodes_image(old_nodes):
    new_nodes = []
    tuple_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            tuple_list = extract_markdown_images(node.text)
            if tuple_list == []:
                new_nodes.append(node)
            else:
                #print(tuple_list)
                sections = []
                curr = node.text
                #print(curr)
                for alt, url in tuple_list:
                    final_md = f"![{alt}]({url})"
                    #print(final_md)
                    sections = curr.split(final_md, 1)
                    left = sections[0]
                    right = sections[1]
                    curr = right                        
                    if left  != "":
                        new_nodes.append(TextNode(left,TextType.TEXT))
                    new_nodes.append(TextNode(alt, TextType.IMAGE, url))
                if curr != "":
                    new_nodes.append(TextNode(curr, TextType.TEXT))
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    tuple_list = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
        else:
            tuple_list = extract_markdown_links(node.text)
            if tuple_list == []:
                new_nodes.append(node)
            else:
                #print(tuple_list)
                sections = []
                curr = node.text
                #print(curr)
                for alt, url in tuple_list:
                    final_md = f"[{alt}]({url})"
                    #print(final_md)
                    sections = curr.split(final_md, 1)
                    left = sections[0]
                    right = sections[1]
                    curr = right                        
                    if left  != "":
                        new_nodes.append(TextNode(left,TextType.TEXT))
                    new_nodes.append(TextNode(alt, TextType.LINK, url))
                if curr != "":
                    new_nodes.append(TextNode(curr, TextType.TEXT))
    return new_nodes

def text_to_text_nodes(text):
    new_nodes = split_nodes_delimiter([text],"**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)

    return new_nodes

def markdown_to_blocks(markdown):
    parts = markdown.split("\n\n")
    blocks = []
    for p in parts:
        s = p.strip()
        if s:
            blocks.append(s)
    return blocks

def block_to_block_type(blocks):
    parts = blocks.split("\n")
    if blocks.startswith("```") and blocks.endswith("```"):
        #print(BlockType.CODE)
        return BlockType.CODE
    
    if re.match(r"^#{1,6} .+\S$", parts[0]):
        #print(BlockType.HEADING)
        return BlockType.HEADING
    all_quote, all_ul, all_ol = True, True, True
    for idx, line in enumerate(parts, start=1):
        all_quote &= line.startswith(">")
        all_ul &= line.startswith("- ")

        j = 0
        while j <len(line) and line[j].isdigit():
            j +=1
        if j == 0:
            all_ol = False
        else:
            all_ol &= j + 1 < len(line) and line[j:j+2] == ". " and int(line[:j]) == idx


    if all_quote:
        #print(BlockType.QUOTE)
        return BlockType.QUOTE
    if all_ul:
        #print(BlockType.UNORDERED_LIST)
        return BlockType.UNORDERED_LIST
    if all_ol:
        #print(BlockType.ORDERED_LIST)
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH   

def text_to_children(text):
    #print(f"[DEBUG INSIDE FUNCTION] Text: {text}")
    nodes = split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes =split_nodes_link(nodes)
    leaf_nodes = []

    for node in nodes:
        leaf_nodes.append(text_node_to_html_node(node))
    
    return leaf_nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children_list = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.CODE:
            stripped_text = block.split("```")
            final_text = stripped_text[1].lstrip()
            text_node = TextNode(final_text, TextType.CODE)
            parent_node = ParentNode("pre",[text_node_to_html_node(text_node)])
            children_list.append(parent_node)
        elif block_type == BlockType.UNORDERED_LIST:
            list_items = block.split("\n")
            list_children_list = []
            for item in list_items:
                modified_item=item.split("- ")
                item_text = modified_item[1]
                li_node = ParentNode("li", text_to_children(item_text))
                list_children_list.append(li_node)
            parent_node = ParentNode("ul",list_children_list)
            children_list.append(parent_node)
        elif block_type == BlockType.ORDERED_LIST:
            list_items = block.split("\n")
            list_children_list = []
            for item in list_items:
                modified_item = item.split(". ")
                item_text = modified_item[1]
                li_node = ParentNode("li", text_to_children(item_text))
                list_children_list.append(li_node)
            parent_node = ParentNode("ol", list_children_list)
            children_list.append(parent_node)
        elif block_type == BlockType.QUOTE:
            list_items = block.split("\n")
            list_children_list = []
            for item in list_items:
                line = item.lstrip()
                if not line.startswith(">"):
                    continue
                content = line[1:].lstrip()
                if not content:
                    continue
                list_children_list.append(text_node_to_html_node(TextNode(content,TextType.TEXT)))
            parent_node = ParentNode(block_type.value, list_children_list)
            children_list.append(parent_node)
        elif block_type == BlockType.HEADING:
            splitted_block= block.split(" ")
            header_type = len(splitted_block[0])
            splitted_text = block.split(header_type * "#")
            final = splitted_text[1].lstrip()
            html_node = text_node_to_html_node(TextNode(final, TextType.TEXT))
            parent_node = ParentNode(f"h{header_type}", [html_node])
            children_list.append(parent_node)
        else:
            modified_block = block.replace("\n", " ")
            html_node = ParentNode(block_type.value, text_to_children(modified_block))
            children_list.append(html_node)


    final_parent = ParentNode("div", children_list)

    return final_parent

def initial_setup(dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.mkdir(dest)
    copy_static_content("static",dest)

def copy_static_content(file_path, dest):
    if not os.path.exists(file_path):
        raise Exception("Error: Path is not existing")
    items_list = os.listdir(file_path)
    print(items_list)
    
    for item in items_list:
        path = os.path.join(file_path, item)
        if os.path.isfile(path):
            shutil.copy(path, dest)
        else:
            os.mkdir(os.path.join(dest,item))
            copy_static_content(path, os.path.join(dest,item))
    
def extract_title(markdown):
    lines = markdown.split("\n")
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("#").strip()
            return title
    raise Exception("There is no h1 header")

def generate_page(from_path, template_path,basepath, output_path):
    #print(basepath)
    print(f"Generating page from {from_path} to {basepath} using {template_path}")

    with open(from_path) as f:
        markdown_content = f.read()
    with open(template_path) as f:
        template = f.read()

    html = template.replace("{{ Title }}", extract_title(markdown_content))
    html = html.replace("{{ Content }}", markdown_to_html_node(markdown_content).to_html())
    html = html.replace('href="/',f'href="{basepath}')
    html = html.replace('src="/',f'src="{basepath}')

    dirpath = os.path.dirname(output_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(html)  

def content_copy(content_path,template_path, dest):
    if not os.path.exists(content_path):
        raise Exception("Error: Path is not existing")
    items_list = os.listdir(content_path)

    for item in items_list:
        path = os.path.join(content_path, item)
        if not os.path.isfile(path):
            new_dest = os.path.join(dest, item)
            os.makedirs(new_dest, exist_ok=True)
            content_copy(path, template_path, new_dest)
        elif path.endswith(".md"):
            out_name = item.replace(".md", ".html")
            out_path = os.path.join(dest, out_name)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            generate_page(path,template_path,out_path)

def generate_pages_recursive(dir_path_content, template_path, basepath, dest_dir_path):
    if not os.path.exists(dir_path_content):
        raise Exception("Error: Path is not existing")

    for item in os.listdir(dir_path_content):
        path = os.path.join(dir_path_content, item)

        if os.path.isdir(path):
            # Recurse into subdir; dest is a directory path
            generate_pages_recursive(path, template_path, basepath, os.path.join(dest_dir_path, item))

        elif os.path.isfile(path) and item.endswith(".md"):
            if item == "index.md":
                output_path = os.path.join(dest_dir_path, "index.html")
            else:
                output_path = os.path.join(dest_dir_path, item.replace(".md", ".html"))
            generate_page(path, template_path, basepath, output_path)


        
