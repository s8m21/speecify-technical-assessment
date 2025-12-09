#!/usr/bin/env python3
"""
SSML (Speech Synthesis Markup Language) is a subset of XML specifically
designed for controlling synthesis. You can see examples of how the SSML
should be parsed in the unit tests below.
"""

#
# DO NOT USE CHATGPT, COPILOT, OR ANY AI CODING ASSISTANTS.
# Conventional auto-complete and Intellisense are allowed.
#
# DO NOT USE ANY PRE-EXISTING XML PARSERS FOR THIS TASK - lxml, ElementTree, etc.
# You may use online references to understand the SSML specification, but DO NOT read
# online references for implementing an XML/SSML parser.
#


from dataclasses import dataclass
from typing import List, Union, Dict

SSMLNode = Union["SSMLText", "SSMLTag"]


@dataclass
class SSMLTag:
    name: str
    attributes: dict[str, str]
    children: list[SSMLNode]

    def __init__(
        self, name: str, attributes: Dict[str, str] = {}, children: List[SSMLNode] = []
    ):
        self.name = name
        self.attributes = attributes
        self.children = children


@dataclass
class SSMLText:
    text: str

    def __init__(self, text: str):
        self.text = text


def parseSSML(ssml: str) -> SSMLNode:
    # TODO: implement this function

    i = 0
    n = len(ssml)
    stack = []
    root = SSMLTag("root", {}, [])
    stack.append(root)
    found_top = False

    while i < n:
        if ssml[i] == "<":

            if ssml.startswith("</", i):
                j = ssml.find(">", i)
                if j == -1:
                    raise Exception("Missing >")
                tag_name = ssml[i+2:j].strip()
                if len(stack) == 1:
                    raise Exception("Extra closing tag")
                current = stack.pop()
                if current.name != tag_name:
                    raise Exception("Mismatched closing tag")
                
                i = j + 1
                continue
            
            j = ssml.find(">", i)
            if j == -1:
                raise Exception("Missing >")
            tag_contents = ssml[i+1:j].strip()
            if not tag_contents:
                raise Exception("Empty tag")

            self_closing = tag_contents.endswith("/")
            if self_closing:
                tag_contents = tag_contents[:-1].rstrip()


            k = 0
            while k < len(tag_contents) and not  tag_contents[k].isspace():
                k += 1
            tag_name = tag_contents[:k]
            attrs_str = tag_contents[k:].strip()

            if not found_top:
                if tag_name != "speak":
                    raise Exception("Missing top-level <speak>")
                found_top = True

            if tag_name == "speak" and len(stack) > 1 and stack[-1].name == "root":
                raise Exception("Multiple top-level tags")
            
            if len(stack) == 1 and len(root.children) >= 1:
                raise Exception("Multi-top level elements are not allowed")

            attrs = {}
            pos = 0
            while pos < len(attrs_str):

                while pos < len(attrs_str) and attrs_str[pos].isspace():
                    pos += 1
                if pos >= len(attrs_str):
                    break


                start = pos
                while (
                    pos < len(attrs_str)
                    and not attrs_str[pos].isspace()
                    and attrs_str[pos] != "="
                ):
                    pos += 1

                name = attrs_str[start:pos]
                if not name:
                    raise Exception("Invalid attribute name")
                
                for ch in name:
                    if not (ch.isalnum() or ch == "_"):
                        raise Exception("Invalid attribute name")

                while pos < len(attrs_str) and attrs_str[pos].isspace():
                    pos += 1
                if pos >= len(attrs_str) or attrs_str[pos] != "=":
                    raise Exception("Missing = in attribute")
                pos += 1

                while pos < len(attrs_str) and attrs_str[pos].isspace():
                    pos += 1
                if pos >= len(attrs_str) or attrs_str[pos] not in ("'", '"'):
                    raise Exception("Attribute value must be double-quoted")
    
                quote = attrs_str[pos]
                pos += 1
                val_start = pos
                while pos < len(attrs_str) and attrs_str[pos] != quote:
                    pos += 1
                if pos >= len(attrs_str):
                    raise Exception("Unterminated attribute value")
            
                value = attrs_str[val_start:pos]
                pos += 1

                attrs[name] = value

            tag = SSMLTag(tag_name, attrs, [])
            stack[-1].children.append(tag)

            if not self_closing:
                stack.append(tag)
            
            i = j + 1

        else:
            
            j = ssml.find("<", i)
            if j == -1:
                j = n
            text = ssml[i:j]

            if text.strip():
                stack[-1].children.append(SSMLText(text))
                
            i = j
    
    if len(stack) != 1:
        raise Exception("Unclosed tag")
    if not root.children:
        raise Exception("Missing <speak>")
    if len(root.children) != 1 or not isinstance(root.children[0], SSMLTag) or root.children[0].name != "speak":
        raise Exception("Missing or invalid top-level <speak> tag")
    return root.children[0]


def ssmlNodeToText(node: SSMLNode) -> str:
    # TODO: implement this function

    if isinstance(node, SSMLText):
        return unescapeXMLChars(node.text)
    

    out = []
    for child in node.children:
        out.append(ssmlNodeToText(child))
    return "".join(out)
   # raise NotImplementedError()


def unescapeXMLChars(text: str) -> str:
    return text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def escapeXMLChars(text: str) -> str:
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

# Example usage:
# ssml_string = '<speak>Hello, <break time="500ms"/>world!</speak>'
# parsed_ssml = parseSSML(ssml_string)
# text = ssmlNodeToText(parsed_ssml)
# print(text)