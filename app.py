from flask import Flask, request, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route('/', methods=['GET'])  # Health check route
def home():
    return "CSV Processing API is running!"

@app.route('/process', methods=['POST'])  # Main API endpoint
def process_csv():
    try:
        # Check if 'file' is in the request
        if 'file' not in request.files:
            return {"error": "No file part in the request"}, 400

        csv_file = request.files['file']

        if csv_file.filename == '':
            return {"error": "No selected file"}, 400

        # Read the uploaded CSV file into a DataFrame
        df = pd.read_csv(csv_file)

        # Check if the required column exists
        if "Oportunidades[Responsavel]" not in df.columns:
            return {"error": "Column 'Oportunidades[Responsavel]' not found."}, 400
        
        # Filter rows based on unique "Responsavel" values
        unique_responsaveis = df["Oportunidades[Responsavel]"].dropna().unique()

        # Create a BytesIO object to hold the CSV output
        output = io.BytesIO()

        # Write the filtered data for each unique "Responsavel" into separate CSV files
        for responsavel in unique_responsaveis:
            # Filter rows based on the "Responsavel"
            filtered_data = df[df["Oportunidades[Responsavel]"] == responsavel]

            if filtered_data.empty:
                continue

            # Write the filtered data to the output CSV file
            filtered_data.to_csv(output, index=False, header=True)
        
        # Reset the pointer to the beginning of the BytesIO object
        output.seek(0)

        # Return the modified CSV data
        return send_file(output, mimetype="text/csv", as_attachment=True, download_name="modified_data.csv")

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
