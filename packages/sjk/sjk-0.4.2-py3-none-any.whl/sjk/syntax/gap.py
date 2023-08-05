#!/usr/bin/env python

import re

token_regex = [
    [re.compile(r';;\s*',      re.M),  "block separator",  ";;"],
    [re.compile(r'(?<!;);\s*', re.M),  "block separator",  ";"],
    [re.compile(r'"',          re.M),  "string delimiter", '"'],
    [re.compile(r"'",          re.M),  "string delimiter", "'"],
    [re.compile(r"\\",         re.M),  "escape character", None],
    [re.compile(r"#",          re.M),  "comment start",    None],
    [re.compile(r"\n",         re.M),  "comment end",      None]
    ]

block_markers= [
    (r"{",      r"}"),
    (r"\[",     r"\]"),
    (r"\(",     r"\)"),
    (r"\bif\b", r"\bfi\b"),
    (r"\bdo\b", r"\bod\b"),
    (r"\bfunction\b", r"\bend\b"),
    (r"\brepeat\b", r"\buntil\b"),
    ]

for i,p in enumerate(block_markers):
  s = re.compile(p[0], re.MULTILINE)
  e = re.compile(p[1], re.MULTILINE)
  token_regex.append([s,"block start", i])
  token_regex.append([e,"block end", i])

def tokenize(input_code):
  tokens = {}
  for pat, t_type, t_subtype in token_regex:
    for m in pat.finditer(input_code):
      i = m.end()-1
      if i not in tokens:
        tokens[i] = []
      tokens[i].append((t_type, t_subtype))
  for i in range(len(input_code)):
    if i in tokens:
      for t_type, t_subtype in tokens[i]:
        yield (i, t_type, t_subtype)
    else:
      yield (i, None, None)

def check(input_code):

  previous_block_separator = 0
  mode = "normal"
  string_type = None
  current_blocks = [None]
  top_level_blocks = []

  for i, t_type, t_subtype in tokenize(input_code):

    if mode == "comment":
      if t_type == "comment end":
        mode = "normal"

    elif mode == "string":
      if t_type == "escape character":
        mode = "escaped"
      elif t_type == "string delimiter":
        if t_subtype == string_type:
          mode = "normal"

    elif mode == "escaped":
      mode = "string"

    else: # mode == "normal"
      if t_type == "comment start":
        mode = "comment"
      elif t_type == "string delimiter":
        string_type = t_subtype
        mode = "string"
      elif t_type == "block start":
        current_blocks.append(t_subtype)
      elif t_type == "block end":
        if current_blocks[-1] == t_subtype:
          current_blocks.pop()
        else:
          mode = "unbalanced delimiters %s" %(i,t_subtype)
          break
      elif t_type == "block separator":
        if len(current_blocks) == 1:
          block_code = input_code[previous_block_separator: i+1]
          top_level_blocks.append((block_code, t_subtype))
          previous_block_separator = i+1

  if len(current_blocks)>1:
    mode = "unbalanced delimiters %s" % current_blocks[1:]

  if previous_block_separator < len(input_code):
    if mode == "normal":
      mode = "missing semicolon"
    top_level_blocks.append((input_code[previous_block_separator:],";"))

  return (mode == "normal", top_level_blocks, mode)

