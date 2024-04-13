# krds-rw
Read and write in Amazon Kindle sidecar file format. These are the files in the `.sdr` folders you see in your Kindle's `ms0:/documents` folder.

## Usage
The KRDS file format is a tree structure that conforms to a schema that defines what data types are allowed and not allowed, what data is mandatory and what is optional, and how the data is structured. (Think XML schemas or JSON schemas.)

### Download the code
Use `git submodule` to add **krds-rw** to your project.

```bash
cd $YOUR_PROJECT_DIR
git submodule init
git submodule add $REPO_URL
git submodule update --recursive

cd $REPO_DIR

git lfs install
git submodule init
git submodule update --recursive
```

In your own project, you can import **krds-rw** as follows.

```python
import os
import sys

# or whichever dir contains $REPO_DIR
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import krdsrw
```

### Using the API
**krds-rw** provides types that subclass Python's built-in types, but represent KRDS data structures.

 - `Bool`
 - `Short`
 - `Int`
 - `Long`
 - `Float`
 - `Double`
 - `Utf8Str`
 - `Array`
 - `Record`
 - `IntMap`
 - `DynamicMap`
 - `DateTime`
 - `Position`
 - `LPR`
 - `ObjectMap`
 - `Store`

These special types:
 - Automatically enforce the KRDS schema. Trying to mutate a container in a way that violates the schema will throw an exception.
 - Transparently convert (think ORM-like) between KRDS data types and Python built-ins. For example, when writing to a container, a Python `int` will automatically be converted to a KRDS `short`, `int`, or `long` based on the container's schema. When reading from a container, a KRDS `short`, `int`, or `long` will automatically be converted to a Python `int`.
 - Being subclasses of Python's built-in containers, you can convert to and from JSON using Python's default `json` module.

`Store` (a subclass of `dict`) is the object that represents the root of a KRDS file. To read and write from `Store`, you need to have some knowledge of the KRDS schema. For ordinary use, it's easiest to learn the schema by printing from the file you want to read.

```python
import json
import krdsrw

root = krdsrw.load_file('the-tempest.yjr')
print(root)

# or with nice indenting
# careful: when dumping to json, booleans will show up as 0 and 1! this is known bug.
json.dumps(root, indent=2)
```

This will output something like the following. You can use this technique to see what's stored in which file and how the data is structured.

```json
{
  "sync_lpr": 1,
  "next.in.series.info.data": "",
  "annotation.cache.object": {
    "notes": [
      {
        "start_pos": {"char_pos": 34461, "chunk_eid": 4429, "chunk_pos": 9},
        "end_pos": {"char_pos": 34473, "chunk_eid": 4429, "chunk_pos": 21},
        "creation_time": 1701678319282,
        "last_modification_time": 1701678319282,
        "template": "0\ufffc0",
        "note": "Most surgeon-like (with reference to Gonzalo as a doctor)."
      }
    ]
  }
}
```

For the full supported schema, see `src/krdsrw/objects.py`.

### Reading from KRDS files
You can read your data using standard Python container access operators. Use `load_file()` to read a KRDS file.

```python
import krdsrw

root = krdsrw.load_file('the-tempest.yjr')

# >>> "Most surgeon-like (with reference to Gonzalo as a doctor)."
print(root['annotation.cache.object']['notes'][0]['note'])
```

### Writing to KRDS files
You can write to KRDS containers as if they were regular Python containers. Use `dump_bytes()` to get the byte representation of a KRDS container.

```python
import krdsrw

root = krdsrw.load_file('the-tempest.yjr')
root['annotation.cache.object']['notes'][0]['note'] = 'I have overwritten this note and here is its replacement.'

with open('the-tempest.yjr', 'wb') as f:
    f.write(krdsrw.dump_bytes(root))
```

#### Dealing with container schemas
Adding a new element (for an array) or entry (for a map) is tricky, because the correct class (plus the schema for that class) depends on its location (key path) within the `Store`. **krds-rw** provides ways to save you from having to manually instantiate the correct class.

For map types, accessing a non-existent key will create a *postulate* in its place. A *postulate* is an element, of the correct class, schema, and necessary default values, automatically created to stand in for an entry that doesn't yet exist. Postulates save you from having to know the correct class and schema for the key path, and also from checking for `KeyError` every time you go down a level in the tree. Upon modifying a postulate, it will be written to its parent container. As long as you don't modify the postulate, it won't become part of its parent container.

```python
import krdsrw

# create empty Store object
root = krdsrw.Store()

# confirm it is in fact empty
# >>> Store{}
print(root)

# we can access root/annotation.cache.object/highlights despite
# neither of them existing

# >>> []
print(root['annotation.cache.object']['highlights'])

# it's still empty
# >>> Store{}
print(root)

# now we modify the postulate at root/annotation.cache.object/highlights
note = root['annotation.cache.object']['highlights'].make_and_append()
note['note'] = 'Here is the text of a new note.'

# because the postulate was modified, it gets written to its parent container
# >>> Store{'annotation.cache.object': IntMap{'highlights': [Record{'start_pos': Position{'char_pos': Int{0}}, 'end_pos': Position{'char_pos': Int{0}}, 'creation_time': DateTime{0ms}, 'last_modification_time': DateTime{0ms}, 'template': Utf8Str{""}}]}}
print(root)
```

You'll notice we used `.make_and_append()` to append to an array. We do this so that we don't have to manually instantiate a class of the correct type, schema, and default values. `.make_and_append()` returns a pointer to the newly-created element, so you can modify it as you want.

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

pip install pytest --pip-args pytest-cov
pytest
```

## Acknowledgements
Thanks to [jhowell](https://www.mobileread.com/forums/showthread.php?t=322172) for his initial work on reverse-engineering the KRDS file format.
