"""Metadatos para compartir en redes (LinkedIn, X...): descripción e imagen
de vista previa de cada página. Las etiquetas se pintan en overrides/main.html."""
import re
from urllib.parse import urljoin

DEFAULT_IMAGE = "assets/images/social.png"
IMG = re.compile(r'<img[^>]+src="([^"]+)"')


def on_page_markdown(markdown, page, config, files, **kwargs):
    m = page.meta.get("machine")
    if m and not page.meta.get("description"):
        info = f"máquina {m.get('difficulty')} de Hack The Box ({m.get('os')})"
        if m.get("status") == "active":
            page.meta["description"] = f"{page.title}, {info}. El write-up se publicará cuando la máquina se retire."
        else:
            page.meta["description"] = (f"Write-up de {page.title}, {info}: enumeración, "
                                        "explotación y escalada de privilegios paso a paso.")
    return markdown


def on_page_content(html, page, config, files, **kwargs):
    # Write-ups publicados: la primera captura (normalmente la de "pwned").
    # Resto de páginas y avisos de máquina activa: la imagen por defecto.
    base = config.site_url or ""
    image = None
    m = page.meta.get("machine")
    if m and m.get("status") != "active":
        for src in IMG.findall(html):
            if not src.startswith(("data:", "http")) and not src.endswith(".svg"):
                image = urljoin(urljoin(base, page.url), src)
                break
    page.meta["og_image"] = image or urljoin(base, DEFAULT_IMAGE)
    return html
