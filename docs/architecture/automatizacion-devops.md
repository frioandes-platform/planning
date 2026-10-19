# Automatización y DevOps: ambientes, pipeline, secretos y cambio

Este documento resume cómo se construye y se cambia la plataforma: qué ambientes hay, cómo se escribe la infraestructura como código, cómo el pipeline lleva un cambio de desarrollo a producción, dónde viven los secretos y cómo se respeta la ventana de cambios de FríoAndes. El código está en el repositorio `frioandes-platform/iac` (Fase 2, issues #20 a #24) y las plantillas de release notes en la Fase 4 (#29 a #31). Aquí está el diseño que ese código implementa, con los nombres de la red, la seguridad y el gobierno ya definidos.

## Contenido

1. Ambientes
2. Infraestructura como código
3. Pipeline y promoción
4. Secretos e identidades del pipeline
5. Estrategia de cambio
6. Verificación
7. Supuestos

---

## 1. Ambientes

| Ambiente | Suscripción | Red | Datos | Quién cambia |
|---|---|---|---|---|
| Desarrollo | `sub-fa-dev` | `10.103.0.0/21` | Sintéticos; sin sensores reales | Desarrolladores en sus grupos de recursos y el pipeline |
| Pruebas | `sub-fa-test` | `10.102.0.0/21` | Sintéticos o anonimizados; sensores simulados | Solo el pipeline; QA ejecuta pruebas |
| Producción | `sub-fa-prod` | `10.101.0.0/21` | Reales | Solo el pipeline, con aprobación; personas solo con PIM y por incidente |
| Hub | `sub-fa-connectivity` | `10.100.0.0/23` | — | Solo el pipeline, con aprobación del equipo de redes |

Los tres ambientes de aplicación tienen la misma estructura (las once subredes de `red-topologia-subnetting.md`, sección 4) y salen del mismo módulo. Cambian el rango, los tamaños y la cantidad de réplicas, no la forma. Así lo que se prueba en pruebas es lo que llega a producción, y lo que dejó de compartir clúster en Cali queda separado por suscripción, identidad y red.

![Ambientes y promoción: el mismo código y la misma imagen pasan de desarrollo a pruebas y a producción](diagramas/ambientes-pipeline.drawio.png)

---

## 2. Infraestructura como código

| Pieza | Qué hace | Fuente que no se copia a mano |
|---|---|---|
| `modules/network` | Red virtual, subredes, NSG y tablas de rutas de un ambiente | `ip-plan.csv`, leído con `csvdecode` (`red-topologia-subnetting.md`, sección 4.9) |
| `modules/security` | Azure Firewall, su política y los grupos de reglas, marcando las temporales de la migración | `firewall-policy.csv` (`red-firewall-y-publicacion.md`, sección 4) |
| `modules/compute` o `modules/ingest` | Un componente de cómputo (Container Apps) o de ingesta (IoT Hub), conectado a la red y la seguridad por referencia | — |
| `environments/dev`, `test` y `prod` | Llaman a los módulos con los valores de cada ambiente | — |

- **Estado remoto, uno por ambiente,** en una cuenta de almacenamiento de su suscripción, con bloqueo y versiones. Un error en el estado de desarrollo no toca producción, y la identidad de desarrollo no puede leer el estado de producción.
- **Etiquetas en el código.** Terraform pone las cinco etiquetas obligatorias (`ambiente`, `carga`, `costo`, `criticidad` y `responsable`) y Azure Policy rechaza lo que llegue sin ellas (`gobierno-landing-zone.md`, sección 5).
- **Continuidad desde el mismo código.** Los entornos de Central US se crean con el mismo módulo cambiando la región (`carga-a-plataforma-logistica.md`, sección 6).
- **El código va en inglés** y la documentación en español, como el resto de la plataforma.

---

## 3. Pipeline y promoción

GitHub Actions, con un GitHub Environment por ambiente:

```
pull request
  → validación: formato, terraform validate, verificadores del plan de direcciones y del firewall
  → terraform plan contra desarrollo, publicado en el pull request
merge a main
  → build y push de las imágenes al registro de contenedores (una vez, con su digest)
  → apply en desarrollo → apply en pruebas, con pruebas automáticas
  → plan de producción → aprobación en el Environment de producción → apply en producción
```

| Regla | Cómo se cumple |
|---|---|
| Promoción controlada | La misma imagen, por su digest, y el mismo código pasan de desarrollo a pruebas y a producción. Nada se construye dos veces |
| Aprobación para producción | El Environment de producción exige la aprobación de dos personas del comité de cambios, con la release note diligenciada |
| Sin despliegue productivo fuera de la ventana | Un paso del pipeline rechaza el apply de producción entre las 04:00 y las 22:00 hora de Colombia y en las fechas de campaña, que lee de un archivo del repositorio. La excepción por incidente exige una etiqueta de incidente y la aprobación de seguridad |
| Ejecutores dentro de la red | Los recursos privados (base, Key Vault, Container Apps internos) se despliegan desde ejecutores autoalojados en `snet-admin` de cada ambiente, separados de las máquinas de operación (`red-acceso-remoto-segunda-nube.md`, sección 2). El build de imágenes puede usar los ejecutores de GitHub |
| Salida controlada de los ejecutores | Solo hacia Azure Resource Manager, Entra ID, GitHub y el registro de contenedores, por el Azure Firewall (reglas FW-303, 306, 309, 312, 315 y 318 de `red-firewall-y-publicacion.md`, sección 4) |

---

## 4. Secretos e identidades del pipeline

- **Sin credenciales duraderas.** Cada ambiente tiene su propia identidad de despliegue en Entra ID, federada con GitHub por OIDC y limitada a su Environment. El repositorio no guarda contraseñas ni claves (`seguridad-iam-cifrado.md`, sección 4).
- **Permisos mínimos.** La identidad de desarrollo solo actúa en `sub-fa-dev`; la de producción solo en `sub-fa-prod` y solo desde el Environment aprobado. Ninguna puede asignar roles fuera de lo que el código declara.
- **Secretos de la aplicación en Key Vault.** Un Key Vault por ambiente (`kv-fa-dev`, `kv-fa-test` y `kv-fa-prod`). Las aplicaciones leen sus secretos con identidad administrada; el pipeline solo escribe los que una herramienta no puede reemplazar por identidad.
- **Auditoría.** Las lecturas y cambios de secretos y los despliegues quedan en el Log Analytics central (`gobierno-auditoria-facturacion.md`).

---

## 5. Estrategia de cambio

| Regla de FríoAndes | Cómo la aplica la plataforma |
|---|---|
| Ningún cambio productivo de 04:00 a 22:00 | Los cambios a producción se aplican de 22:00 a 04:00; el pipeline los bloquea fuera de ese horario |
| Ningún cambio durante una campaña, salvo incidente | El calendario de campañas está en el repositorio y el pipeline lo lee |
| Cada cambio se aprueba, se avisa y se puede deshacer | Release note de aplicación o de infraestructura con qué cambia, la ventana, el impacto, la aprobación, el aviso a despacho y a calidad, y cómo se vuelve atrás (#29 y #30) |

**Cómo se vuelve atrás:**

- **Aplicación.** Container Apps conserva la revisión anterior: volver atrás es mover el tráfico a ella, en minutos y sin desplegar de nuevo. Los cambios de esquema son compatibles hacia atrás, en dos pasos: primero se agrega lo nuevo, y lo viejo se quita en una ventana posterior.
- **Infraestructura.** Se revierte el commit y se aplica de nuevo, por el mismo pipeline y con la misma aprobación. Lo que no se puede deshacer con un apply (borrar datos, retirar una regla de la que depende Cali) se marca así en la release note y necesita una aprobación adicional.
- **Durante la convivencia** la base no admite cambios de esquema: lo que la aplicación necesite para la migración y para Fabric se termina antes del día 0 (`carga-c-migracion-y-campana.md`, sección 3).

---

## 6. Verificación

| Comprobación | Herramienta | Cuándo |
|---|---|---|
| Las direcciones no se solapan con Cali ni entre ambientes | `red/tools/verify_ip_plan.py` | En cada pull request que toque la red |
| Las reglas del firewall respetan el plan y el diseño | `red/tools/verify_firewall_policy.py` | En cada pull request que toque el firewall |
| Lo que Terraform va a crear coincide con el plan de direcciones | `red/tools/compare_tfplan.py` sobre el `plan` | Antes de cada apply |
| El código coincide con la tabla de políticas, regla por regla | Revisión documentada (#21) | Al cerrar el módulo de seguridad |
| El `plan` corre limpio sobre los tres módulos | Evidencia fechada y con el commit (#24) | Al cerrar la Fase 2 |

---

## 7. Supuestos

| Supuesto | Por qué se asume |
|---|---|
| El repositorio de código y el pipeline viven en GitHub | Es donde está el proyecto; los issues #20 a #24 ya lo fijan |
| El estado de Terraform va en una cuenta de almacenamiento por ambiente, en su propia suscripción | Aísla el estado igual que los ambientes |
| La aprobación de producción la dan dos personas del comité de cambios | Separa quien escribe el cambio de quien lo autoriza |
| El calendario de campañas se mantiene en un archivo del repositorio | El pipeline necesita leerlo para bloquear despliegues; las fechas salen de `carga-c-migracion-y-campana.md`, sección 4.1 |
