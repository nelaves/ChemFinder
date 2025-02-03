# app.py
from flask import Flask, render_template, request
import requests
import base64

app = Flask(__name__)

def get_compound_data(compound_name):
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name"
    properties = [
        "IUPACName",
        "MolecularFormula",
        "MolecularWeight",
        "CanonicalSMILES",
        "XLogP"
    ]
    
    try:
        # Get CID (Compound ID)
        cid_response = requests.get(f"{base_url}/{compound_name}/cids/JSON")
        if cid_response.status_code != 200:
            return None, "Compound not found"
        
        cid = cid_response.json()['IdentifierList']['CID'][0]

        # Get compound properties
        props_response = requests.get(
            f"{base_url}/{compound_name}/property/{','.join(properties)}/JSON"
        )
        
        if props_response.status_code != 200:
            return None, "Failed to fetch properties"

        properties_data = props_response.json()['PropertyTable']['Properties'][0]
        
        # Get structure image
        img_response = requests.get(
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        )
        img_base64 = base64.b64encode(img_response.content).decode('utf-8')

        return {
            'name': compound_name,
            'iupac_name': properties_data.get('IUPACName', 'N/A'),
            'molecular_formula': properties_data.get('MolecularFormula', 'N/A'),
            'molecular_weight': properties_data.get('MolecularWeight', 'N/A'),
            'smiles': properties_data.get('CanonicalSMILES', 'N/A'),
            'xlogp': properties_data.get('XLogP', 'N/A'),
            'structure_image': img_base64,
            'cid': cid
        }, None
    
    except Exception as e:
        return None, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        compound_name = request.form['compound']
        data, error = get_compound_data(compound_name)
        return render_template('index.html', data=data, error=error)
    return render_template('index.html', data=None, error=None)

if __name__ == '__main__':
    app.run(debug=True)