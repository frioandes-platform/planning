# Evidencia de planificación simulada — #24

## Alcance y estado

**VALIDACIÓN SIMULADA COMPLETA.** FríoAndes se desarrolla como diseño, sin suscripción de Azure.
El procedimiento ejecuta `terraform validate` y `terraform test` con
`mock_provider "azurerm"`. No se ejecutó el comando independiente
`terraform plan` autenticado, ni se desplegaron recursos en Azure.

El criterio literal de un plan autenticado permanece pendiente. La aceptación
de esta evidencia simulada como equivalente académico corresponde al responsable
de la historia; este documento no afirma que esa aceptación ya exista.

## Identificación de la ejecución

- Repositorio: `frioandes-platform/iac`.
- Commit exacto: [c0944a395c8c3acd6cbdcaee6bd97a244c6f05aa](https://github.com/frioandes-platform/iac/commit/c0944a395c8c3acd6cbdcaee6bd97a244c6f05aa).
- Inicio UTC: `2026-10-21T22:32:26+00:00`.
- Fin UTC: `2026-10-21T22:33:12+00:00`.
- Terraform: `1.16.6`; proveedor fijado por los locks del commit.
- Comando: `bash scripts/check-ingest.sh`.
- Código de salida: `0`.
- Fuente: copia temporal exportada mediante `git archive` del commit indicado.
  No incluye cambios locales, archivos tfvars personales ni estados existentes.

## Resultado por raíz

| Raíz | Pruebas Terraform aprobadas | Resultado |
|---|---:|---|
| `connectivity` | 4 | Aprobadas |
| `dev` | 8 | Aprobadas |
| `test` | 2 | Aprobadas |
| `prod` | 3 | Aprobadas |



## Cobertura de las historias anteriores

- **#20:** integridad de los CSV corregidos, hashes, tres VNets y 33 subredes,
  contención y ausencia de solapamientos con hub, reservas y 23 redes on-premises.
- **#21:** firewall compartido, política, NSG y comparación contra la tabla
  aprobada; reglas temporales solo en escenarios que las seleccionan explícitamente.
- **#22:** contrato del Event Hub, DNS compartido, aislamiento y referencias
  a red y NSG. También se prueban rechazos de configuraciones inválidas.

El escenario `approved_alert_contract` planifica el módulo de ingesta con datos
simulados. `private_alert_ingest_uses_existing_modules` comprueba su integración
con los módulos reales de configuración mediante un **apply simulado**, dentro
de `terraform test`; no constituye un despliegue. `disabled_by_default` por sí
solo no demostraría la cobertura de ingesta.

Las pruebas negativas con `expect_failures` deben pasar porque rechazan lo
previsto. Su éxito no significa que una configuración inválida pueda desplegarse.

## Archivos de evidencia y reproducción

La carpeta adjunta `evidencia-plan-limpio/` contiene `ejecucion.log`, las salidas
JSONL disponibles por raíz y `manifest.json` con los SHA-256, versiones y fechas.
Las salidas proceden exclusivamente de pruebas con valores sintéticos. No se
adjuntan estados, planes binarios autenticados, credenciales ni tfvars reales.

Desde el paquete de captura:

```bash
python3 capturar-evidencia.py --iac /ruta/al/iac --out /ruta/nueva/de/evidencia
```

El commit debe estar disponible localmente; se obtiene con `git fetch origin main`.
La carpeta de salida debe ser nueva. El ejecutor no cambia ramas, no crea commits
y no copia los archivos del paquete encima del repositorio.

## Límites y conclusión

Resultado de las comprobaciones simuladas: **sin errores inesperados**.
No demuestra permisos, cuotas, disponibilidad de nombres, conectividad, DNS real,
lectura/escritura de eventos ni comportamiento del proveedor frente a Azure.
No se presenta esta salida como un `terraform plan` autenticado sin errores.

Referencias: [#24](https://github.com/frioandes-platform/planning/issues/24),
[#20](https://github.com/frioandes-platform/planning/issues/20),
[#21](https://github.com/frioandes-platform/planning/issues/21) y
[#22](https://github.com/frioandes-platform/planning/issues/22).

Documentación técnica: [Terraform provider mocking](https://developer.hashicorp.com/terraform/language/tests/mocking).
