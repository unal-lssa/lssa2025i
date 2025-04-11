**Nancy Vianeth Vera Rodiguez**

### Cambios realizados

#### En el modelo
* Se crearon 2 nuevos backend, para contar con 3 backend en total
* Se creó el componente para el balanceador de carga
* Se crearon los conectores entre el balanceador y cada uno de los backend
* Se creó un conector del frontend al balanceador

#### En transformaciones
* Se genera el balanceador
* Se actualizar la generacion del docker-compose para incluir el balanceador

### Pruebas

* Frontend en ejecución
* Consulta a la Base de Datos
* Validación del balanceo entre los tres backend
