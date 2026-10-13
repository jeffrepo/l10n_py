# l10n_py — Paraguay para Odoo 19

Localización contable base de Ticnova, versión `19.0.1.0.0`.

Incluye el plan de cuentas, diarios iniciales, activación del guaraní PYG e IVA
del 10%, del 5% y exento para compras y ventas, con precios que incluyen IVA.

El addon instalable está en [`l10n_py/`](l10n_py/). Consultar su
[documentación de instalación, alcance y pruebas](l10n_py/README.md).

Esta es la implementación propia de Ticnova; no instalar simultáneamente otra
versión de `l10n_py`, incluida la de OCA. No incluye facturación electrónica
SIFEN ni reportes fiscales DNIT.

Validación inicial: sintaxis, referencias y plantillas verificadas contra el
código de Odoo 19. Las pruebas de integración incluidas requieren ejecutarse
en una base de pruebas de Odoo 19 con PostgreSQL antes de usarlo en producción.
