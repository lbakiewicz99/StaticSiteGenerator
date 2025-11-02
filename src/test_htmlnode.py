import unittest
from functions import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, split_nodes_image, split_nodes_link, text_to_text_nodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title
from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType, BlockType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode("p", "xD", None, {"href": "https://www.google.com", "target": "_blank"})
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"'
        )

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_a(self):
        node = LeafNode("a", "Link", {"href": "www.google.com"})
        self.assertEqual(node.to_html(), '<a href="www.google.com">Link</a>')

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    

    def test_to_html_multiple_children(self):
        node = ParentNode("p",
                          [
                              LeafNode("h1","Header text"),
                              LeafNode(None, "Normal text"),
                              LeafNode("a","link", {"href": "google.com"}),
                              LeafNode("i", "italic text"),
                              LeafNode(None, "Normal text")
                          ])
        self.assertEqual(
            node.to_html(),
            '<p><h1>Header text</h1>Normal text<a href="google.com">link</a><i>italic text</i>Normal text</p>'
        )

    def test_to_html_multiple_children_grandchildren(self):
        node = ParentNode("p",
                          [
                              ParentNode("span", [
                                  LeafNode("p","Paragraph text"),
                                  LeafNode(None,"Normal text")
                              ]),
                              LeafNode(None, "Normal text"),
                              LeafNode("h1","Header"),
                              ParentNode("div",
                                         [
                                             LeafNode("a","link",{"href": "google.com"}),
                                             LeafNode(None,"Normal text")
                                         ]),
                              LeafNode(None,"Normal text")
                          ])
        self.assertEqual(node.to_html(),
                         '<p><span><p>Paragraph text</p>Normal text</span>Normal text<h1>Header</h1><div><a href="google.com">link</a>Normal text</div>Normal text</p>')
        
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

    def test_italic(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is a text node")

    def test_code(self):
        node = TextNode("This is a text node", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "This is a text node")

    def test_link(self):
        node = TextNode("This is a text node", TextType.LINK,"google.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": node.url})
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is a text node", TextType.IMAGE, "picture.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": node.url, "alt": node.text})

    def test_split_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_node = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_node,[
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT)
        ])


    def test_split_bold(self):
        node = TextNode("This is text with a **bold** word", TextType.TEXT)
        new_node = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_node,[
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" word", TextType.TEXT)
        ])

    def test_split_italic(self):
        node = TextNode("This is text with a _italic_ word", TextType.TEXT)
        new_node = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(new_node,[
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word", TextType.TEXT)
        ])

    def test_split_multiple(self):
        node = [TextNode("This is text with a _italic_ word and `code block` new word", TextType.TEXT)]
        node = split_nodes_delimiter(node, "_", TextType.ITALIC)
        node = split_nodes_delimiter(node,"`", TextType.CODE)
        self.assertEqual(node,[
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" new word", TextType.TEXT)
        ])
    
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)


    def test_extract_markdown_images_double(self):
        matches = extract_markdown_images(
            "This is ![images](https://i.imgur.com/zjjcJKZ.png) text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("images", "https://i.imgur.com/zjjcJKZ.png"),("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_none(self):
        matches = extract_markdown_images("This is text with no images")
        self.assertListEqual([], matches)

    def test_extract_markdown_images_with_links(self):
        matches = extract_markdown_images(
            "![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://boot.dev)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)


    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_one_image_at_the_beginning(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_just_an_image(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_one_image_at_the_beginning(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) ![third image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
                TextNode(" ", TextType.TEXT),
                TextNode(
                    "third image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ), 
            ],
            new_nodes,
        )

    def test_split_mix(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) and another [first url](https://i.imgur.com/3elNhQu.png) and ![third image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        new_nodes = split_nodes_link(new_nodes)
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "first url", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "third image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ), 
            ],
            new_nodes,
        )

##########################

    def test_split_link(self):
            node = TextNode(
                "This is text with an [image](https://i.imgur.com/zjjcJKZ.png) and another [second image](https://i.imgur.com/3elNhQu.png)",
                TextType.TEXT,
            )
            new_nodes = split_nodes_link([node])
            self.assertListEqual(
                [
                    TextNode("This is text with an ", TextType.TEXT),
                    TextNode("image", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                    TextNode(" and another ", TextType.TEXT),
                    TextNode(
                        "second image", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                    ),
                ],
                new_nodes,
            )

    def test_split_one_link_at_the_beginning(self):
        node = TextNode(
            "[image](https://i.imgur.com/zjjcJKZ.png) and another [second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_just_an_link(self):
        node = TextNode(
            "[image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_one_link_at_the_beginning(self):
        node = TextNode(
            "[image](https://i.imgur.com/zjjcJKZ.png) and another [second image](https://i.imgur.com/3elNhQu.png) [third image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
                TextNode(" ", TextType.TEXT),
                TextNode(
                    "third image", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ), 
            ],
            new_nodes,
        )

    def test_text_to_text_nodes(self):
        node = TextNode("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)", TextType.TEXT)
        new_nodes = text_to_text_nodes(node)
        self.assertListEqual([
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev")
            ],
            new_nodes
        )

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        markdown_to_blocks(md)

    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# Title"), BlockType.HEADING)

    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```print(hi)```"), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> a\n> b"), BlockType.QUOTE)

    def test_block_to_block_type_ul(self):
        self.assertEqual(block_to_block_type("- a\n- b"), BlockType.UNORDERED_LIST)
    
    def test_block_to_block_type_ol(self):
        self.assertEqual(block_to_block_type("1. a\n2. b\n3. c"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ol_wrong_increment(self):
        self.assertEqual(block_to_block_type("1. a\n3. b"), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("just some text"), BlockType.PARAGRAPH)

    def test_paragraphs(self):
        md = """
# Main header

### Third header

This is **bolded** paragraph
text in a p
tag here

Here is an ![image](google.com)

Here is a [link](google.com)

> "QUOTE"
> 
> --me

This is another paragraph with _italic_ text and `code` here

"""
        self.maxDiff = None
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><h1>Main header</h1><h3>Third header</h3><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>Here is an <img src="google.com" alt="image"></img></p><p>Here is a <a href="google.com">link</a></p><blockquote>"QUOTE"--me</blockquote><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>',
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_extract_title_markdown(self):
        test_string = extract_title("# Hello\nJazda jazda jazda jazda")
        self.assertEqual(test_string, "Hello")

    def test_extract_title_markdown_header_at_the_end(self):
        test_string = extract_title("#Hello\nJazda jazda jazda jazda\nlmao\n# header")
        self.assertEqual(test_string, "header")

    def test_extract_title_markdown_header_in_the_middle(self):
        test_string = extract_title("#Hello\nJazda jazda jazda jazda\nlmao\n# header\nlmao\nlmao")
        self.assertEqual(test_string, "header")

    def test_extract_title_markdown_no_header(self):
        test_string = "#Hello\nJazda jazda jazda jazda\nlmao\n## header\nlmao\nlmao"
        with self.assertRaises(Exception) as ctx:
            extract_title(test_string)
        self.assertIn("h1", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
