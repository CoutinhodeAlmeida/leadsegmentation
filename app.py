from flask import Flask, request, send_file
import pandas as pd
import io
from openpyxl import Workbook

app = Flask(__name__)

@app.route('/', methods=['GET'])  # Health check route
def home():
    return "Excel Processing API is running!"

@app.route('/process', methods=['POST'])  # Main API endpoint
def process_excel():
    try:
        # Check if 'file' is in the request
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        excel_file = request.files['file']

        if excel_file.filename == '':
            return {"error": "No selected file"}, 400

        # Read the uploaded Excel file into a DataFrame
        df = pd.read_excel(excel_file, sheet_name=None)

        # Extract the first sheet (you can adjust as needed)
        sheet_name = "Sheet1"  # Adjust this if needed
        if sheet_name not in df:
            return {"error": f"Worksheet '{sheet_name}' not found."}, 400

        data = df[sheet_name]
        
        # Find the column index for "Oportunidades[Responsavel]"
        responsavel_col_index = data.columns.get_loc("Oportunidades[Responsavel]") if "Oportunidades[Responsavel]" in data.columns else -1
        
        if responsavel_col_index == -1:
            return {"error": "Column 'Oportunidades[Responsavel]' not found."}, 400
        
        # Filter rows based on unique "Responsavel" values
        unique_responsaveis = data["Oportunidades[Responsavel]"].dropna().unique()

        # Create a new Excel workbook to store results
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Add the filtered data for each unique "Responsavel" in a new sheet
            for responsavel in unique_responsaveis:
                # Filter rows based on the "Responsavel"
                filtered_data = data[data["Oportunidades[Responsavel]"] == responsavel]
                
                if filtered_data.empty:
                    continue

                # Write the filtered data to a new sheet with the "Responsavel" name
                filtered_data.to_excel(writer, sheet_name=str(responsavel), index=False)

        output.seek(0)

        # Return the modified Excel file
        return send_file(output, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                         as_attachment=True, download_name="modified_workbook.xlsx")

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)