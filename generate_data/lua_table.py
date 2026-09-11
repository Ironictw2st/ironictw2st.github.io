#!/usr/bin/env python3
"""
Minimal Lua table-literal reader.

Just enough to lift the data tables out of the mod's campaign scripts, which are the real
source of truth for some things the db tables do not express - the AOR recruitment rules
being the one that matters here. It handles the shapes those files actually use:

    { "a", "b" }                 -> ["a", "b"]
    { ["k"] = "v" }              -> {"k": "v"}
    { ["k"] = { "a" } }          -> {"k": ["a"]}
    { ["k"] = true }             -> {"k": True}

and nothing else. It is deliberately not a Lua parser: anything it does not recognise
raises, so a script that changes shape fails loudly instead of yielding half a table.
"""

import re

_WS = " \t\r\n"


def strip_comments(src):
    src = re.sub(r"--\[\[.*?\]\](?:--)?", "", src, flags=re.S)   # block comments
    src = re.sub(r"--[^\n]*", "", src)                           # line comments
    return src


def _skip(s, i):
    while i < len(s) and (s[i] in _WS or s[i] == ","):
        i += 1
    return i


def _string(s, i):
    quote = s[i]
    out, i = [], i + 1
    while s[i] != quote:
        if s[i] == "\\":
            out.append(s[i + 1])
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out), i + 1


def _value(s, i):
    i = _skip(s, i)
    if s[i] == "{":
        return _table(s, i)
    if s[i] in "\"'":
        return _string(s, i)
    m = re.match(r"(true|false|nil|-?\d+(?:\.\d+)?)", s[i:])
    if not m:
        raise ValueError(f"unparsable Lua value at {i}: {s[i:i + 40]!r}")
    tok = m.group(1)
    return {"true": True, "false": False, "nil": None}.get(tok, tok), i + len(tok)


def _table(s, i):
    """-> (list | dict, next index). A table with any keyed entry is read as a dict."""
    assert s[i] == "{"
    i += 1
    items, pairs = [], {}
    while True:
        i = _skip(s, i)
        if i >= len(s):
            raise ValueError("unterminated Lua table")
        if s[i] == "}":
            return (pairs if pairs else items), i + 1
        if s[i] == "[":                                   # ["key"] = value
            key, i = _string(s, _skip(s, i + 1))
            i = _skip(s, i)
            if s[i] != "]":
                raise ValueError(f"expected ] at {i}: {s[i:i + 40]!r}")
            i = _skip(s, i + 1)
            if s[i] != "=":
                raise ValueError(f"expected = at {i}: {s[i:i + 40]!r}")
            val, i = _value(s, i + 1)
            pairs[key] = val
        elif re.match(r"[A-Za-z_]\w*\s*=", s[i:]):        # bare key = value
            m = re.match(r"([A-Za-z_]\w*)\s*=", s[i:])
            val, i = _value(s, i + m.end())
            pairs[m.group(1)] = val
        else:
            val, i = _value(s, i)
            items.append(val)


def read_local(src, name):
    """Value of `local <name> = { ... }`, or None if the file has no such table."""
    src = strip_comments(src)
    m = re.search(r"(?:local\s+)?%s\s*=\s*(?=\{)" % re.escape(name), src)
    if not m:
        return None
    value, _ = _value(src, m.end())
    return value
