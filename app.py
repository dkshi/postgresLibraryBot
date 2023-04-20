import tempfile
from flask import Flask, send_file
import pandas as pd
from database import *


app = Flask(__name__)


@app.route('/download/<book_id>')
def download_statistics(book_id):
    df = pd.DataFrame(db_connector.statistics(book_id)).drop('user_id', axis=1)
    try:
        with tempfile.NamedTemporaryFile(suffix='.xlsx') as tmp:
            filename = f'book_{book_id}_stats.xlsx'
            df.to_excel(tmp.name, index=False)
            return send_file(tmp.name, download_name=filename, as_attachment=True)
    except:
        return 'Failed to download'

