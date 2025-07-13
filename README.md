# etc_data_processing




## 🚀 Requirements

- Python >= 3.9 (i used python==3.11.9)
- [uv](https://pypi.org/project/uv/)

Install **uv** globally:

```bash
pip install uv
```



step 1:
```bash
git clone https://github.com/sazzadJBC/etl_data_processing.git
```

step 2: 

## for virualenv and requirement setup
```bash
uv sync
```
step 3:
### dataset download from s3 bucket

setup the keys and run 

```bash
 uv run download_all_from_s3.py
```

step 4:
```bash
uv run main.py
```

if any library missed, please add by 
```bash
uv add library_name
```

