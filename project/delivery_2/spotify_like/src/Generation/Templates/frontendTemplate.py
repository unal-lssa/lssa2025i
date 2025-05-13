import os
import textwrap
import json  # Importar módulo json


def generate_frontend(name: str, output_dir="skeleton") -> None:
    # Ruta base para el esqueleto del componente
    base_path = f"{output_dir}/{name}"
    os.makedirs(base_path, exist_ok=True)

    # Ruta para la carpeta de contenidos estáticos
    contents_path = os.path.join(base_path, "contents")
    os.makedirs(contents_path, exist_ok=True)

    # --- Generar el archivo index.html dentro de la carpeta 'contents' ---
    html_content = textwrap.dedent(
        """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Reproducción de Música</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <style>
                /* Configuración básica de fuente */
                html,
                body {
                    height: 100%;
                    margin: 0;
                    padding: 0;
                }

                #app {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    opacity: 1;
                    backdrop-filter: blur(2px);
                }

                /* Ajustar el fondo para que cubra toda la pantalla */
                body {
                    background-color: #e5e5f7;
                    background-image: radial-gradient(#4591f7 1.3px, #e5e5f7 1.3px);
                    background-size: 26px 26px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }

                h1 {
                    opacity: 1;
                }
            </style>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        </head>

        <body>
            <div id="app" class="container mx-auto p-6 md:p-10 lg:p-14 rounded-xl text-center max-w-2xl w-full">
                <h1 class="text-4xl md:text-5xl font-bold mb-6 text-purple-900">
                    Tu Música, Tu Experiencia
                </h1>
                <p class="text-lg md:text-xl text-gray-900 mb-8 leading-relaxed">
                    Explora un universo de sonidos. Crea tus listas, descubre nuevos artistas y lleva tu música a donde vayas.
                </p>
                <div class="flex flex-col md:flex-row justify-center gap-6">
                    <a href="player.html" class="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 shadow-lg">
                        Iniciar Sesión
                    </a>
                    <a href="player.html" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 shadow-lg">
                        Registrarse
                    </a>
                </div>
                <p class="mt-12 text-gray-500 text-sm">
                </p>
            </div>
        </body>

        </html>
    """
    )

    html_content_player = textwrap.dedent(
        """
            <!DOCTYPE html>
            <html lang="en">

            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sistema de Reproducción de Música - Reproductor</title>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    /* Configuración básica de fuente */
                    body {
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    }

                    html,
                    body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        overflow: hidden;
                        /* Ocultar scrollbar si el contenido no cabe, común en players */
                    }

                    #player-layout {
                        display: flex;
                        width: 100%;
                        height: 100vh;
                        /* Ocupar toda la altura visible */
                        background-color: rgba(31, 41, 55, 0.8);
                        /* Fondo semi-transparente para el layout principal */
                        backdrop-filter: blur(2px);
                        /* Efecto de desenfoque */
                    }

                    #sidebar {
                        width: 250px;
                        /* Ancho fijo para la sidebar */
                        background-color: rgba(17, 24, 39, 0.9);
                        /* Fondo más oscuro para la sidebar */
                        padding: 1.5rem;
                        display: flex;
                        flex-direction: column;
                        gap: 1rem;
                        overflow-y: auto;
                        /* Scroll si el contenido de la sidebar es largo */
                    }

                    #main-content {
                        flex-grow: 1;
                        /* Ocupar el espacio restante */
                        padding: 1.5rem;
                        overflow-y: auto;
                        /* Scroll si el contenido principal es largo */
                        display: flex;
                        flex-direction: column;
                    }

                    #player-bar {
                        height: 80px;
                        /* Altura fija para la barra del reproductor */
                        background-color: rgba(55, 65, 81, 0.9);
                        /* Fondo para la barra del reproductor */
                        width: 100%;
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        padding: 0 1.5rem;
                        flex-shrink: 0;
                        /* Evita que se encoja */
                    }

                    /* Media query para hacer la sidebar responsive */
                    @media (max-width: 768px) {

                        /* En pantallas pequeñas (md en Tailwind) */
                        #player-layout {
                            flex-direction: column;
                            /* Apilar sidebar y contenido */
                        }

                        #sidebar {
                            width: 100%;
                            /* Sidebar ocupa todo el ancho */
                            height: auto;
                            /* Altura automática */
                            flex-direction: row;
                            /* Items de la sidebar en fila */
                            justify-content: space-around;
                            padding: 1rem;
                        }

                        #main-content {
                            padding: 1rem;
                            flex-grow: 1;
                            /* Ocupar espacio restante */
                        }

                        #player-bar {
                            padding: 0 1rem;
                        }
                    }
                </style>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
            </head>

            <body class="text-white">
                <div id="player-layout">
                    <div id="sidebar" class="text-gray-300">
                        <h2 class="text-xl font-bold text-white mb-4 md:mb-0">Navegación</h2>
                        <a href="#" class="hover:text-white transition duration-200">Inicio</a>
                        <a href="#" class="hover:text-white transition duration-200">Explorar</a>
                        <a href="#" class="hover:text-white transition duration-200">Tu Biblioteca</a>
                        <a href="#" class="hover:text-white transition duration-200">Crear Lista</a>
                        <div class="mt-auto md:mt-0">
                            <a href="index.html" class="text-sm text-gray-400 hover:text-white transition duration-200">Volver a
                                Inicio</a>
                        </div>
                    </div>

                    <div id="main-content">
                        <div class="flex-grow p-4 md:p-6 bg-gray-700 rounded-lg shadow-inner">
                            <h2 class="text-2xl font-bold mb-4 text-purple-300">Explorar Música</h2>
                            <p>Contenido dinámico del reproductor irá aquí (ej: listas, álbumes, etc.).</p>
                            <div class="mt-6 space-y-4">
                                <div class="p-4 bg-gray-600 rounded-md flex items-center gap-4">
                                    <div class="w-12 h-12 bg-gray-500 rounded-md"></div>
                                    <div>
                                        <div class="font-semibold">Nombre de la Canción</div>
                                        <div class="text-sm text-gray-400">Artista - Álbum</div>
                                    </div>
                                </div>
                                <div class="p-4 bg-gray-600 rounded-md flex items-center gap-4">
                                    <div class="w-12 h-12 bg-gray-500 rounded-md"></div>
                                    <div>
                                        <div class="font-semibold">Otra Canción</div>
                                        <div class="text-sm text-gray-400">Otro Artista - Otro Álbum</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div id="player-bar" class="mt-auto">
                            <div class="flex items-center gap-4">
                                <div class="w-10 h-10 bg-gray-500 rounded-md"></div>
                                <div>
                                    <div class="text-sm font-semibold">Felp 22, Duki, Rauw Alejandro - TRAPPERZ A Mafia Da Sicilia (feat. MC Davo & Fuego)</div>
                                    <div class="text-xs text-gray-400">Felp 22</div>
                                </div>
                            </div>
                            <div class="text-xl text-gray-300 flex gap-6">
                            <audio controls>
                                <source src="http://localhost:8080/music-storage/song.mp3" type="audio/mpeg">
                                Tu navegador no soporta el elemento de audio.
                            </audio>
                            </div>
                        </div>
                    </div>
                </div>
            </body>

            </html>
    """
    )

    # --- Generar el archivo app.js ---
    # Este app.js solo servirá los archivos HTML estáticos desde 'contents'
    app_code = textwrap.dedent(
        """
        const express = require('express');
        const path = require('path'); // Importar módulo path
        const app = express();

        // Servir archivos estáticos desde la subcarpeta 'contents' (donde están los HTML)
        app.use(express.static(path.join(__dirname, 'contents')));


        // Ruta para la landing page (servir index.html)
        // Esta ruta específica sigue siendo necesaria para que '/' cargue index.html
        app.get('/', (req, res) => {
            res.sendFile(path.join(__dirname, 'contents', 'index.html'));
        });

        // Nota: No necesitamos una ruta específica para player.html porque
        // express.static (el segundo app.use) ya lo sirve cuando se solicita por nombre de archivo.

        // Definir el puerto de escucha
        const PORT = 80; // Puerto interno del contenedor

        app.listen(PORT, () => console.log(`Frontend running on port ${PORT}`));
    """
    )

    # --- Generar el archivo package.json ---
    # Solo necesitamos express, ya que axios no se usa en esta versión básica
    dependencies = {
        "express": "^4.18.2",
    }

    package_json_content = {
        "name": name.lower(),  # Nombre del paquete en minúsculas
        "version": "1.0.0",
        "main": "app.js",
        "dependencies": dependencies,
    }

    # --- Generar el archivo Dockerfile ---
    dockerfile_content = textwrap.dedent(
        """
        FROM node:18

        WORKDIR /app

        # Copiar package.json y package-lock.json (si existe) primero para optimizar el cache de Docker
        COPY package*.json ./

        RUN npm install

        # Copiar el resto de los archivos de la aplicación (incluyendo app.js y la carpeta contents)
        COPY . .

        # El frontend escucha en el puerto 80 dentro del contenedor
        EXPOSE 80

        CMD ["node", "app.js"]
    """
    )

    # --- Escribir los archivos ---
    with open(os.path.join(contents_path, "index.html"), "w") as f:
        f.write(html_content)

    with open(os.path.join(contents_path, "player.html"), "w") as f:
        f.write(html_content_player)  # Escribir el contenido del player.html

    with open(os.path.join(base_path, "app.js"), "w") as f:
        f.write(app_code)

    with open(os.path.join(base_path, "package.json"), "w") as f:
        # Usar json.dump para escribir el diccionario package_json_content
        json.dump(package_json_content, f, indent=2)

    with open(os.path.join(base_path, "Dockerfile"), "w") as f:
        f.write(dockerfile_content)
