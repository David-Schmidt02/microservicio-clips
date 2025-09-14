import os
import json

def renombrar_videos(directorio="videos"):
    if not os.path.exists(directorio):
        print(f"La carpeta '{directorio}' no existe.")
        return
    
    archivos = sorted(os.listdir(directorio))
    mapping = {}
    contador = 1

    for archivo in archivos:
        ruta_vieja = os.path.join(directorio, archivo)

        # Ignorar subcarpetas
        if not os.path.isfile(ruta_vieja):
            continue

        # Solo trabajar con .mp4
        if archivo.lower().endswith(".mp4"):
            nuevo_nombre = f"video_{contador}.mp4"
            ruta_nueva = os.path.join(directorio, nuevo_nombre)

            os.rename(ruta_vieja, ruta_nueva)
            mapping[nuevo_nombre] = archivo  # guardar referencia

            print(f"✔ {archivo} → {nuevo_nombre}")
            contador += 1

    # Guardar el log de renombrado
    if mapping:
        with open("videos_renombrados.json", "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=4, ensure_ascii=False)
        print("\n📄 Mapeo guardado en 'videos_renombrados.json'")

if __name__ == "__main__":
    renombrar_videos("videos")
