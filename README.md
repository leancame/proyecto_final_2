# Proyecto Asistente Virtual

## 3. Diseño

### 3.1 Descripción del Diseño

Este proyecto está diseñado como un asistente virtual modular que integra múltiples componentes para ofrecer funcionalidades avanzadas de interacción por voz, búsqueda, inteligencia artificial y gestión de tareas. La arquitectura se basa en la separación clara de responsabilidades en módulos independientes que interactúan mediante interfaces bien definidas:

- **Módulo de Voz:** Gestiona la entrada y salida de voz, permitiendo al usuario comunicarse con el asistente mediante comandos hablados. Este módulo se encarga de la síntesis y reconocimiento de voz, facilitando una experiencia natural e intuitiva.
- **Módulo de Comandos:** Contiene comandos específicos que el asistente puede ejecutar. Estos comandos se implementan como plugins que se cargan dinámicamente al iniciar el asistente, lo que permite extender y mantener el sistema fácilmente sin modificar el núcleo.
- **Módulo de Servicios:** Proporciona servicios auxiliares como acceso a bases de datos, integración con APIs externas (por ejemplo, Google Calendar, buscadores web), y otros recursos necesarios para la ejecución de comandos.
- **Módulo de Inteligencia Artificial:** Incluye diferentes modelos de IA que pueden ser seleccionados según el entorno o necesidad, para procesar y generar respuestas inteligentes. Esto permite adaptar el rendimiento y capacidad del asistente según los recursos disponibles.

Esta estructura modular facilita la escalabilidad, mantenibilidad y flexibilidad del sistema, permitiendo incorporar nuevas funcionalidades o modificar las existentes sin afectar el funcionamiento global.

#### Esquema de Diseño Modular

```
+-------------------+
|   Módulo de Voz   |
| (Entrada/Salida)  |
+---------+---------+
          |
          v
+---------+---------+
|  Módulo de Comandos|
| (Plugins dinámicos)|
+---------+---------+
          |
          v
+---------+---------+
|  Módulo de Servicios|
| (Bases de datos,    |
|  APIs externas)     |
+---------+---------+
          |
          v
+---------+---------+
| Módulo de IA       |
| (Modelos inteligentes)|
+-------------------+
```

### 3.1.1 Selección de la Arquitectura del Sistema

Se ha optado por una arquitectura modular y orientada a servicios, basada en los siguientes principios:

- **Separación de responsabilidades:** Cada módulo tiene una función clara y definida, lo que mejora la organización del código y facilita el mantenimiento.
- **Carga dinámica de comandos:** Los comandos se implementan como plugins que se descubren y cargan en tiempo de ejecución, permitiendo extender el asistente sin modificar su núcleo.
- **Interacción basada en eventos de voz:** El sistema escucha comandos de voz, los procesa y ejecuta la acción correspondiente, proporcionando una experiencia de usuario fluida y natural.
- **Uso de servicios externos:** La integración con APIs externas y bases de datos se realiza a través de servicios especializados, lo que permite desacoplar la lógica del asistente de las dependencias externas.

Esta arquitectura permite que el asistente sea adaptable, extensible y robusto, facilitando la incorporación de nuevas tecnologías y funcionalidades en el futuro.

#### Esquema de Arquitectura del Sistema

```
+-------------------+       +-------------------+
|   Entrada de Voz  | ----> |  Procesamiento de  |
|  (Reconocimiento) |       |    Comandos       |
+-------------------+       +---------+---------+
                                      |
                                      v
                            +---------+---------+
                            | Servicios y APIs  |
                            | (Bases de datos,  |
                            |  Google Calendar) |
                            +---------+---------+
                                      |
                                      v
                            +---------+---------+
                            |  Módulo de IA     |
                            | (Modelos y lógica)|
                            +-------------------+
```

### 3.1.2 Selección de la Base de Datos

Para la gestión de tareas y almacenamiento de datos persistentes, se ha seleccionado una base de datos relacional MySQL, accesible mediante el ORM SQLAlchemy. Las razones de esta elección incluyen:

- **Robustez y madurez:** MySQL es un sistema de gestión de bases de datos relacional ampliamente utilizado y probado, que garantiza estabilidad y rendimiento.
- **Flexibilidad y facilidad de uso:** SQLAlchemy proporciona una capa de abstracción que facilita la definición de modelos de datos, consultas y manejo de transacciones, permitiendo trabajar con la base de datos de forma más intuitiva y segura.
- **Escalabilidad:** La combinación de MySQL y SQLAlchemy permite escalar la aplicación y mantener la integridad de los datos en entornos con múltiples servicios y módulos.
- **Compatibilidad:** La elección de MySQL facilita la integración con otras herramientas y servicios que puedan ser necesarios en el futuro.

#### Esquema de Selección de Base de Datos

```
+-------------------+
|    MySQL          |
| (Base de datos    |
|  relacional)      |
+---------+---------+
          |
          v
+---------+---------+
|   SQLAlchemy ORM  |
| (Abstracción y    |
|  manejo de datos) |
+-------------------+
```

---

### 3.2 Explicación de la Carga Dinámica y Patrón de Comando

El asistente virtual utiliza un patrón de diseño modular que permite la carga dinámica de comandos, facilitando la extensión y mantenimiento del sistema sin modificar el núcleo principal.

- **Carga Dinámica:**
  - Al iniciar, el asistente explora el paquete `asistente.comando` para descubrir todos los módulos de comandos disponibles.
  - Utiliza la librería `pkgutil` para iterar sobre los módulos y `importlib` para importarlos dinámicamente.
  - Cada módulo es inspeccionado para encontrar clases que heredan de `BaseComando`, la clase base para todos los comandos.
  - Se crean instancias de estas clases y se almacenan en una lista de comandos activos.

- **Patrón de Comando:**
  - Cada comando implementa métodos como `activar` para determinar si debe responder a un comando de voz específico, y `ejecutar` para realizar la acción correspondiente.
  - Cuando el asistente recibe un comando de voz, itera sobre los comandos cargados y llama a `activar` para identificar el comando adecuado.
  - El comando identificado ejecuta su lógica mediante el método `ejecutar`.
  - También se soporta un método `detener` para interrumpir comandos en ejecución si es necesario.

Este enfoque permite agregar nuevos comandos simplemente creando nuevos módulos que extiendan `BaseComando`, sin necesidad de modificar el código central del asistente.

---
Este diseño modular y flexible garantiza que el asistente virtual sea escalable, mantenible y fácil de extender con nuevas funcionalidades.

### 3.3 Esquema de Flujo de la Aplicación

A continuación se presenta un esquema de flujo que muestra cómo funciona la aplicación de manera general, desde la entrada de voz hasta la ejecución de comandos y generación de respuestas:

```
+-------------------+
|   Entrada de Voz   |
| (Reconocimiento)   |
+---------+---------+
          |
          v
+---------+---------+
| Procesamiento de  |
|    Comandos       |
| (Activación y     |
|  Ejecución)       |
+---------+---------+
          |
          v
+---------+---------+
| Servicios y APIs  |
| (Bases de datos,  |
|  Google Calendar) |
+---------+---------+
          |
          v
+---------+---------+
|  Módulo de IA     |
| (Generación de    |
|  Respuestas)      |
+---------+---------+
          |
          v
+---------+---------+
|   Salida de Voz   |
| (Síntesis)        |
+-------------------+
```

Este flujo representa el ciclo completo de interacción del asistente virtual, desde que el usuario habla hasta que recibe una respuesta hablada, pasando por la activación de comandos, consulta a servicios y generación de respuestas inteligentes.
