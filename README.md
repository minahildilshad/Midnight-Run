# Midnight Run

An 8-second stylized 3D coupe animation: camera orbit, spinning alloy spokes, moving road markings, cyan headlights and magenta runway lighting.

## Watch
Open Midnight_Run.mp4 in a video player. The included preview was produced with a standalone Python 3D renderer, not Blender. It is 960 x 540, 24 fps, and has no audio.

## Generate the editable Blender scene
Use Blender 4.2 or later. Keep midnight_run_blender.py and scene.json together in the extracted folder.

1. Open Blender and select the Scripting workspace.
2. In the Text Editor, choose Open and select midnight_run_blender.py.
3. Click Run Script. It replaces the current scene, so start with a new file.
4. The script creates the car geometry, materials, lights and keyframed animation and saves Midnight_Run.blend beside the script.
5. Press Play on the timeline, or choose Render > Render Animation to render 192 PNG frames at 1280 x 720.

The Blender script passed Python syntax checks but could not be executed here because Blender was unavailable. Its Cycles lighting and reflections will differ from the standalone preview.

With FFmpeg installed, convert the rendered PNG sequence into an MP4:

```sh
ffmpeg -framerate 24 -i frames/frame_%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart Midnight_Run_Blender.mp4
```

## Optional standalone renderer
With Python, NumPy, Pillow and FFmpeg installed:

```sh
python create_scene.py
python render_preview.py
```

The standalone renderer expects a sibling deliverables folder. Blender rendering does not use these Python dependencies.

All geometry is procedural and editable. No branded car models, external assets or accounts are required.

## Deploy the video website to Vercel

Extract this ZIP and upload all files and the `public` folder to your GitHub
repository root, replacing existing files. Upload the folder's contents with
the folder structure intact. Do not upload the ZIP itself.

The `public` folder contains `index.html` and `Midnight_Run.mp4`. The root
`vercel.json` serves that folder without an install or build step. The Blender
scripts remain available in the repository for local editing.

In Vercel, keep Root Directory `./`, choose Application Preset Other, and leave
build overrides disabled. Commit the GitHub upload, then redeploy the latest
commit. Your homepage will show the video with playback controls and download.
