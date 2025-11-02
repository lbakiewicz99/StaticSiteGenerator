from textnode import TextNode, TextType
from functions import copy_static_content, initial_setup, generate_page, content_copy, generate_pages_recursive
import sys

def main():
    basepath = sys.argv[1] if len(sys.argv)>=2 else "/"
    relative_path_static = "static"
    output_dir = "docs"
    relative_path_content = "content"
    initial_setup(output_dir)
    generate_pages_recursive(relative_path_content, "template.html", basepath, output_dir)
main()