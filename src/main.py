from textnode import TextNode, TextType
from functions import copy_static_content, initial_setup, generate_page, content_copy, generate_pages_recursive

def main():
    relative_path_static = "static"
    relative_path_public = "public"
    relative_path_content = "content"
    initial_setup(relative_path_public)
    generate_pages_recursive(relative_path_content, "template.html", relative_path_public)
main()