# Using `save_triple_signals.py` with Google Colab

This guide explains how to use the `save_triple_signals.py` script in a Google Colab environment to generate trading signal data and load it for analysis.

## Prerequisites

*   A Google Account (for using Google Colab).
*   Access to the MySQL database that `save_triple_signals.py` uses, and the necessary credentials (host, user, password, database name).

## Steps

### 1. Upload Files to Colab

1.  Open a new Colab notebook or an existing one.
2.  In the Colab interface, go to the "Files" tab in the left sidebar.
3.  Click the "Upload to session storage" button (icon with an upward arrow).
4.  Upload the following files from your local `aipha/programs/stable/` directory:
    *   `save_triple_signals.py`
    *   Create a new directory `aipha/logs` in your Colab environment if the script is configured to write logs there and you want to keep them. (The script currently tries to log to `aipha/logs/triple_signals.log`). You can create `mkdir -p aipha/logs`.

### 2. Create a `.env` File for Database Credentials

The script uses a `.env` file to load database credentials.

1.  In the Colab "Files" tab, click the "New file" button (icon that looks like a page).
2.  Name the file `.env`.
3.  Open the newly created `.env` file and add your database credentials like this:

    ```
    MYSQL_HOST=your_database_host
    MYSQL_USER=your_database_user
    MYSQL_PASSWORD=your_database_password
    MYSQL_DATABASE=your_database_name
    ```
    Replace `your_database_host`, etc., with your actual credentials.

    **Security Note:** Be cautious with your credentials. If you share your Colab notebook, avoid sharing the cell that creates the `.env` file or the file itself if it contains sensitive information. For more robust security, consider using Colab's "Secrets" feature for storing sensitive data.

### 3. Install Dependencies

Open a new code cell in your Colab notebook and run the following commands to install the necessary Python packages:

```python
!pip install mysql-connector-python python-dotenv
```

### 4. Run `save_triple_signals.py`

1.  Open a new code cell.
2.  You can now run the script. To save the output to a CSV file, use the `--output-csv` flag followed by the desired filename.

    ```python
    !python save_triple_signals.py --symbol BTCUSDT --timeframe 5m --output-csv btc_signals.csv
    ```

    *   Replace `BTCUSDT` and `5m` with the symbol and timeframe you are interested in.
    *   `btc_signals.csv` will be the name of the output file. You can change it.

3.  After the script finishes, you should see `btc_signals.csv` (or your chosen filename) in the Colab "Files" tab. You can download it from there if needed.

### 5. Load and Analyze Data in Pandas

1.  Once the CSV file is generated, you can easily load it into a Pandas DataFrame for analysis. Open a new code cell and run:

    ```python
    import pandas as pd

    # Load the generated CSV file
    df_signals = pd.read_csv('btc_signals.csv')

    # Display the first few rows of the DataFrame
    print(df_signals.head())

    # Display information about the DataFrame
    print(df_signals.info())

    # Example: Filter signals with a combined_score > 0.7
    # high_score_signals = df_signals[df_signals['combined_score'] > 0.7]
    # print(f"
Found {len(high_score_signals)} signals with combined_score > 0.7:")
    # print(high_score_signals)
    ```

### 6. Using the `TripleSignalSaver` Class Logic (Advanced)

If you want to use the script's internal logic (e.g., the `TripleSignalSaver` class and its methods) directly within your Colab notebook, you have a couple of options:

**Option A: Copy-Pasting Class Definition**

1.  You can open `save_triple_signals.py` in a text editor or in Colab's file viewer.
2.  Copy the entire `TripleSignalSaver` class definition.
3.  Paste it into a code cell in your Colab notebook.
4.  You'll also need to ensure all necessary imports used by the class are present in your notebook (e.g., `os`, `sys`, `logging`, `mysql.connector`, `datetime`, `dotenv`, `csv`, `json`).
5.  You would then instantiate and use the class:

    ```python
    # Make sure .env is loaded if you haven't run the script directly
    # from dotenv import load_dotenv
    # load_dotenv() # Loads .env file from the current directory

    # saver = TripleSignalSaver()
    # if saver.connect():
    #     # Example: Find signals (this doesn't save to DB or CSV unless you call save_signals)
    #     raw_signals = saver.find_triple_signals('BTCUSDT', '5m')
    #     print(f"Found {len(raw_signals)} raw signals.")
    #
    #     processed_signals = []
    #     if raw_signals:
    #         for signal in raw_signals:
    #             strength, strength_details = saver.calculate_signal_strength(signal)
    #             combined, combined_details = saver.calculate_combined_score(signal, strength_details)
    #             # ... (add more processing as done in the original save_signals)
    #             # This part is more involved as you'd replicate parts of save_signals logic
    #
    #     # Or, to use the full save_signals logic (including DB and CSV write):
    #     # success = saver.save_signals('BTCUSDT', '5m', output_csv_filename='custom_signals.csv')
    #     # print(f"Signal saving process successful: {success}")
    #
    #     saver.close()
    ```

**Option B: Importing the script (More Complex Setup)**

   If `save_triple_signals.py` is structured as a module (which it currently is, mostly), you could try importing it. However, scripts that are also designed to be run directly with `argparse` and `if __name__ == "__main__":` can sometimes be tricky to import cleanly without triggering their main execution block or if they have side effects upon import (like logging setup).

   For simplicity in Colab, copy-pasting the class or specific functions you need (Option A) is often more straightforward if you only need parts of the functionality. If you need the full script's behavior as a library, more significant refactoring of `save_triple_signals.py` to separate library code from executable code would be ideal.

## Troubleshooting

*   **`ModuleNotFoundError`**: Ensure you've run `!pip install` for all dependencies.
*   **Database Connection Errors**: Double-check your `.env` file for correct credentials and ensure the database is accessible from Colab's IP range (this might require configuring firewall rules on your database server).
*   **File Not Found when running script**: Make sure `save_triple_signals.py` and your `.env` file are in the root directory of your Colab session (i.e., directly under "Files" and not in a subfolder, unless you adjust paths in your commands).
*   **Log file path**: The script is configured to write logs to `aipha/logs/triple_signals.log`. If this path doesn't exist, logging to file might fail. You can create it with `!mkdir -p aipha/logs` in a Colab cell or modify the script's logging configuration if you prefer a different path or behavior.
