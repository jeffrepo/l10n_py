# l10n_py — Paraguay - Contabilidad base (Odoo 19)

Localización inicial para una **empresa nueva de Paraguay**. Utiliza las
plantillas nativas de `account.chart.template`, como `l10n_gt`, con código
`py`. Depende únicamente de `account` y puede utilizarse sin Enterprise.

Existe una localización comunitaria de OCA con el mismo nombre técnico
`l10n_py`. Esta es una implementación independiente: **no colocar ambas
versiones en las rutas de addons del mismo servidor** ni sustituir una por la
otra en una base ya configurada sin planificar una migración.

## Contenido

- Moneda guaraní (`base.PYG`, símbolo ₲), reutilizada y activada por Odoo al
  cargar el plan. Su redondeo nativo es de ₲1, sin decimales monetarios.
- 47 cuentas de seis dígitos y 21 grupos: disponibilidades, clientes,
  proveedores, IVA, inventario, activos, pasivos, patrimonio, ingresos,
  costos y gastos. Odoo añade sus cuentas técnicas de cobros y pagos pendientes.
- Cuentas predeterminadas de clientes, proveedores, ingresos, costos,
  diferencias de cambio, diferencias de caja y transferencias internas.
- Diarios de ventas (`VEN`), compras (`COM`), banco (`BNK`), caja (`CSH`),
  operaciones diversas (`VAR`), diferencias de cambio (`DIF`) e impuestos en
  base a efectivo (`ICEF`). Este último es un diario técnico estándar;
  los impuestos de la plantilla se reconocen al facturar, no al cobrar.
- IVA 10%, IVA 5% y exento, separados para ventas y compras: seis impuestos.
  El valor predeterminado de compras y ventas es IVA 10%.
- Cuentas distintas para crédito y débito fiscal al 10% y 5%, y cuentas para
  saldo a favor e IVA por pagar. Facturas y notas de crédito tienen repartos
  contables definidos.

Los precios **incluyen IVA**, igual que en la plantilla de Guatemala consultada.
Ejemplos con una unidad y sin descuentos:

| Impuesto | Precio ingresado | Base | IVA | Total |
| --- | ---: | ---: | ---: | ---: |
| IVA 10% | ₲110.000 | ₲100.000 | ₲10.000 | ₲110.000 |
| IVA 5% | ₲105.000 | ₲100.000 | ₲5.000 | ₲105.000 |
| Exento | ₲100.000 | ₲100.000 | ₲0 | ₲100.000 |

Si las listas de precios de la empresa son netas, cambiar la opción «Incluido en
el precio» de los impuestos antes de cargar productos y comenzar a facturar.
El 5% y la exención deben asignarse a los productos u operaciones que
correspondan; la plantilla no decide su tratamiento fiscal automáticamente.

## Instalación y configuración

1. Clonar este repositorio en una carpeta llamada `l10n_py` dentro de una
   ruta de addons de Odoo 19 (por ejemplo, `/ruta/addons/l10n_py`). El manifiesto
   `__manifest__.py` y el resto del módulo están directamente en la raíz del
   repositorio. Incluir `/ruta/addons` en `addons_path`, reiniciar el servicio
   y actualizar la lista de aplicaciones.
2. Crear una empresa independiente con país **Paraguay**. No crearla como
   sucursal de otra empresa: las sucursales heredan el plan y la
   moneda de su empresa raíz.
3. Seleccionar la empresa paraguaya e instalar **Paraguay - Contabilidad base**.
   Si no se carga automáticamente, en Contabilidad → Configuración → Ajustes
   → Localización fiscal, seleccionar **Paraguay - Contabilidad base** y guardar
   (el nombre del país depende del idioma).
4. Verificar PYG, IVA predeterminado, cuentas y diarios. Completar datos de
   empresa/RUC, cuentas bancarias reales y métodos de pago, incluidas sus
   cuentas de cobros y pagos pendientes según el flujo de conciliación.
5. Revisar con el contador local el plan propuesto, las tasas por producto y
   las cuentas de cada operación antes de usarlo en producción.

La instalación pone la plantilla a disposición de las empresas. Su selección
carga datos por empresa mediante los identificadores estándar de Odoo. No hay
un script que recorra o modifique todas las empresas. Los productos compartidos
pueden recibir el impuesto predeterminado de la nueva empresa mediante el flujo
normal de Odoo, conservando los impuestos de sus otras empresas.

Esta plantilla está destinada al arranque de una empresa sin movimientos. Para
una empresa que ya tiene un plan o asientos, se necesita una migración contable;
no basta con cambiar de paquete fiscal. El módulo no cambia la definición
global de PYG ni introduce tipos de cambio inventados.

## Alcance de esta primera versión

Es una base contable para Paraguay, no un plan oficial aprobado ni una
localización fiscal completa. No incluye SIFEN/e-Kuatia, timbrados, numeración
fiscal paraguaya, validación del dígito verificador del RUC, declaraciones DNIT,
libros fiscales, retenciones, IRE, ISC ni liquidación automática del IVA. La
numeración de los diarios es la interna de Odoo y no acredita validez fiscal.

Incluye la cuenta de inventario para registros contables; la valoración
automática de existencias requiere configurar Inventario y sus categorías.
Los diarios de caja y banco utilizan los mecanismos estándar de pagos y
conciliación de Odoo, que deben configurarse para la operativa de cada empresa.

## Pruebas

La validación inicial de sintaxis, referencias y plantillas se realizó contra
el código de Odoo 19. Las pruebas de integración aún deben ejecutarse en una
base de pruebas de Odoo 19 con PostgreSQL antes de usarlo en producción.

En una base desechable con Odoo 19 y PostgreSQL:

```sh
odoo-bin -c /ruta/odoo.conf -d paraguay_test \
  -i l10n_py --without-demo=all \
  --test-enable --test-tags /l10n_py --stop-after-init
```

Para una base de pruebas donde el módulo ya está instalado, sustituir `-i` por
`-u`. Las rutas de addons de la configuración deben incluir el directorio
padre de la carpeta `l10n_py` y los addons estándar de Odoo.

Las pruebas cubren carga de moneda y valores predeterminados, diarios, cálculo
de los seis impuestos, publicación de facturas y notas de crédito de compras
y ventas, recarga sin duplicados y separación entre empresas. Activan
`l10n_check_fields_complete` para detectar referencias a campos incompatibles.

## Referencias

- [Plantilla de Guatemala, Odoo 19](https://github.com/odoo/odoo/tree/19.0/addons/l10n_gt).
- [Cargador de planes, Odoo 19](https://github.com/odoo/odoo/blob/19.0/addons/account/models/chart_template.py).
- [Monedas nativas, incluido PYG](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/data/res_currency_data.xml).
- [DNIT: cartilla informativa del IVA, artículo 90 de la Ley 6380/19](https://www.dnit.gov.py/documents/20123/224724/Cartilla%2BInformativa%2Bsobre%2Bel%2BIVA.pdf/13824efd-fcdb-2414-4eec-dec790a7f00f?t=1684507476257.pdf).
- [Localización comunitaria de OCA](https://github.com/OCA/l10n-paraguay/tree/19.0/l10n_py).
