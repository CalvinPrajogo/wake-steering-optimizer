# test_nrel_api.py
"""
Quick NREL API test with clearer dependency error messages.
"""
from datetime import datetime

try:
    import requests
except ImportError:
    print("Missing dependency: 'requests'. Install with: pip install -r requirements.txt")
    raise

try:
    import pandas as pd
except ImportError:
    print("Missing dependency: 'pandas'. Install with: pip install -r requirements.txt")
    raise


def test_nrel_connection(api_key):
    """
    Test if NREL API is working
    """
    print("Testing NREL Wind Toolkit API...")
    
    # JSON API endpoint (gives structured metadata and is easier to parse)
    url = "https://developer.nrel.gov/api/wind-toolkit/v2/wind/wtk-download"
    
    # Example location: Iowa wind farm region
    # Use your personal email found in the file (string literal) and construct WKT

    # Single-coordinate example (you can loop many coordinates using fetch_many_locations)
    lat = 41.5
    lon = -93.5
    email = 'leonardodgarcia25@gmail.com'

    # Validate interval (allowed: 5, 15, 30, 60)
    interval = 15
    if interval not in {5, 15, 30, 60}:
        raise ValueError('interval must be one of 5,15,30,60')

    attrs = ['wind_speed', 'wind_direction', 'temperature', 'pressure']

    params = {
        'api_key': api_key,
        'email': email,
        'wkt': f'POINT ({lon} {lat})',
        'hubheight': 100,
        'years': 2012,
        'interval': interval,
        'utc': 'false',
        'leap_day': 'false',
        'attributes': ','.join(attrs),
        'outputformat': 'JSON'
    }

    print('Using request params:')
    for k, v in params.items():
        print(f"  {k}: {v}")

    # Helper: fetch JSON with retries and exponential backoff
    def fetch_location_json(url, params, max_retries=3, timeout=60):
        backoff = 1.0
        for attempt in range(max_retries):
            try:
                r = requests.get(url, params=params, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except requests.exceptions.RequestException as e:
                print(f"Request attempt {attempt+1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(backoff)
                backoff *= 2

    # Parser: convert NREL WTK JSON into a tidy DataFrame
    def parse_wtk_json_to_df(obj, attrs_requested=None):
        # Robustly search for data blocks (list-of-dicts or list-of-lists) inside JSON
        def find_data(o):
            # If list-of-dicts, return it
            if isinstance(o, list) and o and isinstance(o[0], dict):
                return o
            # If list-of-lists, return it
            if isinstance(o, list) and o and isinstance(o[0], list):
                return o
            # If dict, search values
            if isinstance(o, dict):
                for k, v in o.items():
                    res = find_data(v)
                    if res is not None:
                        return res
            return None

        if not isinstance(obj, dict):
            raise ValueError('Unexpected JSON structure')

        data_block = find_data(obj.get('outputs', obj))
        if data_block is None:
            # last attempt: search entire object
            data_block = find_data(obj)

        if data_block is None:
            # helpful debug info
            top = {k: (type(v).__name__) for k, v in obj.items()}
            raise ValueError(f'No data block found in JSON response. Top-level keys and types: {top}')

        # If list-of-dicts -> direct DataFrame
        if isinstance(data_block, list) and data_block and isinstance(data_block[0], dict):
            df = pd.DataFrame(data_block)
            return df

        # Else list-of-lists
        df = pd.DataFrame(data_block)

        # Attempt to get attribute names from metadata
        attrs = None
        if 'outputs' in obj and isinstance(obj['outputs'], dict):
            # sometimes attributes live under outputs->attributes
            out = obj['outputs']
            if 'attributes' in out and isinstance(out['attributes'], list):
                attrs = out['attributes']
        if attrs is None and 'metadata' in obj and isinstance(obj['metadata'], dict):
            if 'attributes' in obj['metadata'] and isinstance(obj['metadata']['attributes'], list):
                attrs = obj['metadata']['attributes']

        if attrs is None and attrs_requested is not None:
            attrs = attrs_requested

        if attrs is not None and len(attrs) == df.shape[1]:
            df.columns = attrs
        else:
            # Try naming first five as date/time if appropriate
            if df.shape[1] >= 5:
                possible_dt = ['year', 'month', 'day', 'hour', 'minute']
                df.columns = possible_dt + [f'var_{i}' for i in range(df.shape[1] - 5)]

        # Construct timestamp if possible
        if set(['year', 'month', 'day', 'hour', 'minute']).issubset(df.columns):
            try:
                df['timestamp'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute']])
            except Exception:
                pass

        return df

    try:
        print("Sending request to NREL (JSON endpoint)...")
        import time
        obj = fetch_location_json(url, params)
        print("✅ Received JSON response")

        # Quick inspect
        print("Top-level keys:", list(obj.keys()) if isinstance(obj, dict) else type(obj))

        # Print a short summary of 'outputs' structure to help parsing
        if 'outputs' in obj and isinstance(obj['outputs'], dict):
            outs = obj['outputs']
            print("Outputs keys:")
            for k, v in outs.items():
                t = type(v).__name__
                if isinstance(v, dict):
                    inner = list(v.keys())[:10]
                    print(f"  {k}: {t}, keys: {inner}...")
                elif isinstance(v, list):
                    ln = len(v)
                    first_type = type(v[0]).__name__ if ln else 'empty'
                    print(f"  {k}: list ({ln}), first_item_type: {first_type}")
                else:
                    print(f"  {k}: {t}")

        # If the JSON response returns a download URL, fetch that CSV
        outs = obj.get('outputs', {})
        download_url = outs.get('downloadUrl') if isinstance(outs, dict) else None
        if download_url:
            print('Found downloadUrl in JSON outputs, fetching CSV...')
            dlr = requests.get(download_url, timeout=120)
            dlr.raise_for_status()
            content = dlr.content

            # Save raw download
            raw_file = 'nrel_wtk_2012_100m_raw'
            # If ZIP, save as .zip and extract CSV
            from io import BytesIO, StringIO
            import zipfile

            if content[:2] == b'PK':
                raw_zip = raw_file + '.zip'
                with open(raw_zip, 'wb') as f:
                    f.write(content)
                print(f'Saved raw ZIP: {raw_zip} (size: {len(content)} bytes)')

                z = zipfile.ZipFile(BytesIO(content))
                # assume first file is the CSV
                name_list = z.namelist()
                if not name_list:
                    raise ValueError('ZIP archive is empty')
                inner_name = name_list[0]
                print(f'Extracting {inner_name} from ZIP')
                csv_bytes = z.read(inner_name)
                try:
                    csv_text = csv_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    csv_text = csv_bytes.decode('latin1')

            else:
                # plain text response
                try:
                    csv_text = content.decode('utf-8')
                except Exception:
                    csv_text = content.decode('latin1')

            # Save raw CSV (decoded)
            raw_csv_file = raw_file + '.csv'
            with open(raw_csv_file, 'w', encoding='utf-8') as f:
                f.write(csv_text)
            print(f'Saved raw CSV: {raw_csv_file} (size: {len(csv_text)} bytes)')

            # Try to parse CSV: many WTK CSVs have two header comment rows
            try:
                df = pd.read_csv(StringIO(csv_text), skiprows=2)
            except Exception:
                # fallback: no skiprows
                df = pd.read_csv(StringIO(csv_text))

            print(f"\n✅ Parsed {len(df)} rows from CSV into DataFrame")
            print("Columns:", list(df.columns))
            print(df.head())

            # Save tidy CSV
            out_file = 'nrel_wtk_2012_100m_tidy.csv'
            df.to_csv(out_file, index=False)
            print(f"Saved tidy CSV: {out_file}")

            return True

        # Otherwise try to parse JSON inline
        df = parse_wtk_json_to_df(obj, attrs_requested=attrs)
        print(f"\n✅ Parsed {len(df)} rows into DataFrame")
        print("Columns:", list(df.columns))
        print(df.head())

        # Save tidy CSV
        out_file = 'nrel_wtk_2012_100m_tidy.json_parsed.csv'
        df.to_csv(out_file, index=False)
        print(f"Saved tidy CSV: {out_file}")

        return True

    except requests.exceptions.HTTPError as e:
        # Print more detailed info from the response body if available
        resp = e.response
        try:
            content = resp.text
        except Exception:
            content = '<unable to read response content>'

        print(f"❌ HTTP Error: {e} (status {resp.status_code})")
        print("Request URL:", getattr(e.request, 'url', '<no url>'))
        print("Response body:")
        print(content)
        return False

    except requests.exceptions.RequestException as e:
        # Generic requests error
        print(f"❌ Error: {e}")
        return False

# Run test
if __name__ == "__main__":
    API_KEY = input("Enter your NREL API key: ")
    test_nrel_connection(API_KEY)