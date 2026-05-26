import ast
import json
import re
from pathlib import Path


TRANSLATIONS_DIR = Path("/app/superset/translations")
DOMAIN = "superset"


def parse_po_string(value):
    return ast.literal_eval(value)


def parse_header(value):
    header = {"domain": DOMAIN, "lang": "en", "plural_forms": "nplurals=2; plural=(n != 1)"}
    for line in value.splitlines():
        if line.startswith("Language:"):
            header["lang"] = line.split(":", 1)[1].strip()
        elif line.startswith("Plural-Forms:"):
            header["plural_forms"] = line.split(":", 1)[1].strip()
    return header


def parse_po(path):
    entries = []
    entry = {}
    current = None

    def finish():
        nonlocal entry, current
        if "msgid" in entry:
            entries.append(entry)
        entry = {}
        current = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            finish()
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid_plural "):
            current = "msgid_plural"
            entry[current] = parse_po_string(line[len("msgid_plural ") :])
            continue
        if line.startswith("msgid "):
            current = "msgid"
            entry[current] = parse_po_string(line[len("msgid ") :])
            continue
        if line.startswith("msgstr["):
            match = re.match(r"msgstr\[(\d+)\]\s+(.*)", line)
            if match:
                index = int(match.group(1))
                entry.setdefault("msgstr_plural", {})[index] = parse_po_string(match.group(2))
                current = ("msgstr_plural", index)
            continue
        if line.startswith("msgstr "):
            current = "msgstr"
            entry[current] = parse_po_string(line[len("msgstr ") :])
            continue
        if line.startswith('"') and current is not None:
            value = parse_po_string(line)
            if isinstance(current, tuple):
                entry[current[0]][current[1]] += value
            else:
                entry[current] += value

    finish()
    return entries


def build_language_pack(locale):
    po_path = TRANSLATIONS_DIR / locale / "LC_MESSAGES" / "messages.po"
    if not po_path.exists():
        raise FileNotFoundError(po_path)

    catalog = {"": {"domain": DOMAIN, "lang": locale}}
    for entry in parse_po(po_path):
        msgid = entry.get("msgid", "")
        if msgid == "":
            catalog[""] = parse_header(entry.get("msgstr", ""))
            continue
        if "msgstr_plural" in entry:
            plural_values = entry["msgstr_plural"]
            values = [entry.get("msgid_plural", "")]
            values.extend(plural_values[index] for index in sorted(plural_values))
        else:
            translated = entry.get("msgstr", "")
            if not translated:
                continue
            values = [translated]
        catalog[msgid] = values

    language_pack = {"domain": DOMAIN, "locale_data": {DOMAIN: catalog}}
    output_path = TRANSLATIONS_DIR / locale / "LC_MESSAGES" / "messages.json"
    output_path.write_text(
        json.dumps(language_pack, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Wrote {output_path} with {len(catalog) - 1} translations.")


def main():
    for locale in ("ru",):
        build_language_pack(locale)


if __name__ == "__main__":
    main()
