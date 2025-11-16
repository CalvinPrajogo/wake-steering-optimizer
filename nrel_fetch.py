"""
nrel_fetch.py

Helper script to fetch NREL Wind Toolkit data for arbitrary latitude/longitude pairs.

Usage:
  - Provide a CSV with columns `lat,lon` (header optional) using `--coords-file coords.csv`.
  - Or pass a single coordinate with `--lat LAT --lon LON`.

The script calls the JSON endpoint, follows `downloadUrl` when present (handles ZIP),
parses the CSV into a pandas DataFrame, tags rows with `lat` and `lon`, and appends to
an output CSV `nrel_wtk_combined.csv` (default).

Notes:
  - Include your `API_KEY` and `EMAIL` when running; both are required by the API.
  - The script uses polite rate-limiting and retries with exponential backoff.
"""

import time
import requests
import pandas as pd
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
import argparse


def sanitize_filename(s: str) -> str:
    return "".join(c for c in s if (c.isalnum() or c in ('-', '_', '.')))


def fetch_location(api_key, email, lat, lon, hubheight=100, years=2012, interval=60, attrs=None, max_retries=3, pause=1.0):
    """Fetch one location and return a tidy pandas DataFrame (with lat/lon columns).
    This will follow a downloadUrl and extract ZIP if necessary.
    """
    URL = "https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-download"
    attrs = attrs or ['wind_speed', 'wind_direction', 'temperature', 'pressure']

    params = {
        'api_key': api_key,
        'email': email,
        'wkt': f'POINT ({lon} {lat})',
        'hubheight': hubheight,
        'years': years,
        'interval': interval,
        'utc': 'false',
        'leap_day': 'false',
        'attributes': ','.join(attrs),
        'outputformat': 'JSON'
    }

    backoff = 1.0
    for attempt in range(max_retries):
        try:
            r = requests.get(URL, params=params, timeout=60)
            r.raise_for_status()
            obj = r.json()
            break
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(backoff)
            backoff *= 2

    outputs = obj.get('outputs', {})
    download_url = outputs.get('downloadUrl') if isinstance(outputs, dict) else None

    # Prepare filenames for saving raw files per location
    base = f"nrel_{years}_{hubheight}m_{lat:.4f}_{lon:.4f}"
    base = sanitize_filename(base)
    Path('nrel_raw').mkdir(exist_ok=True)

    if download_url:
        dl = requests.get(download_url, timeout=120)
        dl.raise_for_status()
        content = dl.content

        # If ZIP, extract
        if content[:2] == b'PK':
            zip_path = Path('nrel_raw') / (base + '.zip')
            zip_path.write_bytes(content)
            z = zipfile.ZipFile(BytesIO(content))
            name_list = z.namelist()
            inner = name_list[0]
            csv_bytes = z.read(inner)
            try:
                csv_text = csv_bytes.decode('utf-8')
            except UnicodeDecodeError:
                csv_text = csv_bytes.decode('latin1')
            csv_path = Path('nrel_raw') / (base + '.csv')
            csv_path.write_text(csv_text, encoding='utf-8')
        else:
            # plain text
            try:
                csv_text = content.decode('utf-8')
            except Exception:
                csv_text = content.decode('latin1')
            csv_path = Path('nrel_raw') / (base + '.csv')
            csv_path.write_text(csv_text, encoding='utf-8')

        # Parse CSV: many WTK CSVs have comment header rows; try skiprows=2 then fallback
        try:
            df = pd.read_csv(StringIO(csv_text), skiprows=2)
        except Exception:
            df = pd.read_csv(StringIO(csv_text))

    else:
        # Try to parse inline JSON data
        # search for data block
        data_block = None
        if 'data' in obj and isinstance(obj['data'], list):
            data_block = obj['data']
        elif 'outputs' in obj and isinstance(obj['outputs'], dict):
            out = obj['outputs']
            # try common shapes
            for k in ('data', 'values', 'collection'):
                if k in out:
                    data_block = out[k]
                    break

        if data_block is None:
            # as a last resort, raise with debug info
            raise ValueError('No inline data or downloadUrl found in NREL response')

        # data_block may be list-of-dicts or list-of-lists
        if data_block and isinstance(data_block[0], dict):
            df = pd.DataFrame(data_block)
        else:
            df = pd.DataFrame(data_block)
            # apply attribute names if present
            attrs_meta = None
            if 'metadata' in obj and isinstance(obj['metadata'], dict):
                attrs_meta = obj['metadata'].get('attributes')
            if attrs_meta and len(attrs_meta) == df.shape[1]:
                df.columns = attrs_meta

    # Tag with lat/lon for merging later
    df['lat'] = lat
    df['lon'] = lon

    # polite pause between requests
    time.sleep(pause)
    return df


def fetch_many(api_key, email, coords, out_file='nrel_wtk_combined.csv', **kwargs):
    frames = []
    for lat, lon in coords:
        print(f'Fetching for {lat},{lon} ...')
        df = fetch_location(api_key, email, lat, lon, **kwargs)
        frames.append(df)

    if frames:
        combined = pd.concat(frames, ignore_index=True)
        combined.to_csv(out_file, index=False)
        print(f'Saved combined CSV: {out_file} ({len(combined)} rows)')
    else:
        print('No data fetched.')


def parse_coords_file(path: str):
    p = Path(path)
    df = pd.read_csv(p, header=None)
    # accept either two columns (lat,lon) or named
    if df.shape[1] >= 2:
        return [(float(r[0]), float(r[1])) for r in df.iloc[:, :2].itertuples(index=False, name=None)]
    else:
        raise ValueError('Coords file must have at least two columns: lat,lon')


def main():
    parser = argparse.ArgumentParser(description='Fetch NREL WTK data for a set of lat/lon points')
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--coords-file', help='CSV file with lat,lon per row')
    parser.add_argument('--lat', type=float)
    parser.add_argument('--lon', type=float)
    parser.add_argument('--out', default='nrel_wtk_combined.csv')
    parser.add_argument('--hubheight', type=int, default=100)
    parser.add_argument('--years', type=int, default=2012)
    parser.add_argument('--interval', type=int, default=60)
    args = parser.parse_args()

    coords = []
    if args.coords_file:
        coords = parse_coords_file(args.coords_file)
    elif args.lat is not None and args.lon is not None:
        coords = [(args.lat, args.lon)]
    else:
        # interactive prompt
        print('Enter lat,lon pairs (one per line). Blank to finish:')
        while True:
            line = input().strip()
            if not line:
                break
            parts = [p.strip() for p in line.split(',')]
            coords.append((float(parts[0]), float(parts[1])))

    if not coords:
        print('No coordinates provided; exiting.')
        return

    fetch_many(args.api_key, args.email, coords, out_file=args.out, hubheight=args.hubheight, years=args.years, interval=args.interval)


if __name__ == '__main__':
    main()
