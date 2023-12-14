# krdsrw
Read and write in Amazon Kindle sidecar file format. These are the the files in the `.sdr` folders you see in your Kindle's `ms0:/documents` folder.

## Developing
```bash
cd "$REPO_DIR"

git lfs install

git submodule init
git submodule update --recursive

python -m venv .venv
source .venv/scripts/activate.sh

pip install pre-commit
pre-commit install --install-hooks

python -m build --wheel ./krdsrw/

pip install pytest --pip-args pytest-cov
pytest
pytest --cov=krdsrw
```

## Credits
By midrare.

Extra thanks to [jhowell](https://www.mobileread.com/forums/showthread.php?t=322172) for his initial work on reverse-engineering the KRDS file format.
