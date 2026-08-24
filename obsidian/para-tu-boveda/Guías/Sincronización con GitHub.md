# Sincronización de la bóveda con GitHub

Tu bóveda vive en el repo privado `sebavillalba22/obsidian`. Con esto
lográs tres cosas: respaldo de todas tus notas, la misma bóveda en PC y
celular, y que Claude pueda leer y escribir tus notas desde cualquier
sesión (pushea a `main` y el plugin Git te lo baja solo).

## Publicar tu bóveda por primera vez (una sola vez, en tu PC)

**Antes que nada:** copiá el archivo `.gitignore` del kit a la carpeta raíz
de tu bóveda (evita sincronizar estado local que genera conflictos entre
dispositivos).

### Opción A — GitHub Desktop (sin terminal)

1. Instalá [GitHub Desktop](https://desktop.github.com) e iniciá sesión.
2. **File → Add local repository** → elegí la carpeta de tu bóveda → como
   no es un repo todavía, te ofrece **"create a repository here"** → aceptá
   (Initialize Git LFS: no hace falta).
3. Botón **Publish repository** → Name: `obsidian` → dejá tildado **Keep
   this code private** → Publish.

### Opción B — Terminal (PowerShell)

Necesitás [Git](https://git-scm.com/download/win) instalado. Primero creá
el repo vacío en [github.com/new](https://github.com/new): nombre
`obsidian`, **Private**, sin README. Después:

```powershell
cd "C:\ruta\a\tu\boveda"
git init -b main
git add .
git commit -m "bóveda inicial"
git remote add origin https://github.com/sebavillalba22/obsidian.git
git push -u origin main
```

Al pushear se abre el navegador para autorizar con tu cuenta de GitHub.

### Darle acceso a Claude

En [claude.ai](https://claude.ai) → Settings → Connectors → GitHub:
verificá que la app tenga acceso al repo `obsidian` (si al instalarla
elegiste "solo repos seleccionados", agregalo a la lista).

## Plugin Git en la PC (sincronización automática)

1. Obsidian → Ajustes → **Community plugins** → Turn on community plugins.
2. Browse → buscá **"Git"** → Install → Enable.
3. En las opciones del plugin:
   - **Commit-and-sync interval**: 10 (minutos)
   - **Pull on startup**: activado
4. Listo. Para forzar una sincronización ya: Ctrl+P → "Git: Commit-and-sync".

## En el celular

1. Instalá Obsidian (Android/iOS) y creá una bóveda vacía cualquiera (es
   solo para poder entrar a los ajustes).
2. Necesitás un **token de GitHub**: en github.com → tu foto → Settings →
   **Developer settings** → Personal access tokens → **Fine-grained tokens**
   → Generate new token:
   - Nombre: `obsidian-celular` · Expiración: la más larga posible
   - Repository access: **Only select repositories** → `obsidian`
   - Permissions → Repository permissions → **Contents: Read and write**
   - Generate y **copiá el token** (no se vuelve a mostrar).
3. En Obsidian: activá community plugins e instalá **Git** (igual que en PC).
4. Ctrl+P / tirar hacia abajo → comando **"Git: Clone an existing remote
   repo"**:
   - URL: `https://github.com/sebavillalba22/obsidian.git`
   - Usuario: `sebavillalba22` · Contraseña: **el token**
5. Configurá el mismo commit-and-sync automático que en la PC.

> En bóvedas muy grandes el plugin en el celular puede ponerse lento (usa
> una implementación de Git propia). Si pasa, subí el intervalo de sync.

## Problemas típicos

- **Conflicto de edición**: si editaste la misma nota en dos lados sin
  sincronizar, el plugin avisa y deja marcas `<<<<<<<` en la nota. Abrila,
  quedate con la versión buena y borrá las marcas.
- **El token venció**: el celular deja de sincronizar sin drama; generá un
  token nuevo y cargalo en las opciones del plugin (Authentication).
- **Claude no ve el repo**: revisá el acceso de la app de GitHub de Claude
  (paso "Darle acceso a Claude").

Ver también: [[Conexión local con Claude MCP]]
