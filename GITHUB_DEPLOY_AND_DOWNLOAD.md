# GitHub Build + Download Guide

## Current environment limitation
Attempting to clone your GitHub repository from this environment failed with:
`CONNECT tunnel failed, response 403`.

So I cannot push directly to `https://github.com/huskanovile-lab/trading-ai.git` from here.

## What I prepared for you
I added a bundle script that creates downloadable project archives:

```bash
bash scripts/create_download_bundle.sh
```

Generated files are placed in:
- `dist/*.zip`
- `dist/*.tar.gz`

## How to publish to your GitHub repo from your machine
1. Download the zip/tar from `dist/`.
2. Extract it locally.
3. In the extracted folder run:

```bash
git init
git remote add origin https://github.com/huskanovile-lab/trading-ai.git
git add .
git commit -m "Import autonomous trading AI project"
git push -u origin main
```

## Reproducible local startup
Backend (seed + run):
```bash
bash scripts/start_backend.sh
```

Frontend:
```bash
bash scripts/start_frontend.sh
```


## Additional repository clone attempt
Tried cloning:
- `https://github.com/huskanovile-lab/Gbg-codex-trading.git`

Result in this environment:
- `CONNECT tunnel failed, response 403`

## Optional slim release package
Create a curated release folder + zip:
```bash
bash scripts/create_release_folder.sh
```
Outputs:
- `dist/release-package/`
- `dist/release-package.zip`


## Windows note (`bash` not recognized)
If you are in Windows CMD/PowerShell and get:
`'bash' is not recognized as an internal or external command`
use:
- `scripts\start_backend_windows.bat`
- `scripts\start_frontend_windows.bat`


### Python build error on Windows (`pydantic-core`)
If pip tries to compile `pydantic-core` and fails with Rust/Cargo errors, you are likely on an unsupported Python build for available wheels.
Use Python **3.12** and run:
- `scripts\start_backend_windows.bat`
