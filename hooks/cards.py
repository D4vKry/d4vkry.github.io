"""Genera las tarjetas de 'Últimos write-ups' de la portada a partir de la
ficha (front matter `machine`) de cada write-up de HTB."""
from datetime import datetime
from pathlib import Path

from mkdocs.utils.meta import get_data

MARKER = "<!-- dk:ultimos-writeups -->"
MAX_CARDS = 6
OS_ICON = {"windows": "microsoft-windows"}


def _date(value):
    try:
        return datetime.strptime(str(value), "%d/%m/%Y")
    except ValueError:
        return datetime.min


def on_page_markdown(markdown, page, config, files, **kwargs):
    if MARKER not in markdown:
        return markdown

    items = []
    for f in files.documentation_pages():
        if not f.src_uri.startswith("HTB/"):
            continue
        _, meta = get_data(Path(f.abs_src_path).read_text(encoding="utf-8"))
        machine = meta.get("machine")
        if not machine:
            continue
        title = meta.get("title") or Path(f.src_uri).parent.name
        items.append((_date(machine.get("date")), title, f.src_uri, machine))
    items.sort(key=lambda i: i[0], reverse=True)

    cards = []
    for _, title, uri, m in items[:MAX_CARDS]:
        diff = str(m.get("difficulty", ""))
        os_name = str(m.get("os", ""))
        active = m.get("status") == "active"
        icon = "lock-outline" if active else OS_ICON.get(os_name.lower(), "linux")
        line = f'<span class="dk-card-diff {diff.lower()}">{diff}</span> · {os_name} · {m.get("date", "")}'
        if active:
            line += ' · <span class="dk-card-lock">Máquina activa</span>'
        cards.append(f"-   :material-{icon}: **[{title}]({uri})**\n\n    {line}\n")

    grid = '<div class="grid cards" markdown>\n\n' + "\n".join(cards) + "\n</div>"
    return markdown.replace(MARKER, grid)
