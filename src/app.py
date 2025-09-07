from flask import Flask, request, render_template, jsonify
import joblib
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import json
import uuid
from standardization import GemStandardizer

app = Flask(__name__)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging with rotating file handler
log_file = os.path.join(logs_dir, 'gem_price_predictions.log')
handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)  # 10MB per file, keep 5 backups
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - [%(session_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))

# Create logger
logger = logging.getLogger('gem_price_predictor')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# Create session context filter
class SessionContextFilter(logging.Filter):
    def filter(self, record):
        record.session_id = getattr(record, 'session_id', 'NO_SESSION')
        return True

logger.addFilter(SessionContextFilter())

def log_prediction(session_id, input_data, prediction=None, error=None):
    """Helper function to log prediction details"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id,
        'input_data': input_data,
        'prediction': prediction,
        'error': str(error) if error else None
    }
    
    if error:
        logger.error(json.dumps(log_data), extra={'session_id': session_id})
    else:
        logger.info(json.dumps(log_data), extra={'session_id': session_id})

# Load the model
try:
    model = joblib.load('../models/gem_price_global.pkl')
    print("Model loaded successfully")  # Console debug output
    logging.info("Model loaded successfully")
except Exception as e:
    error_msg = f"Error loading model: {str(e)}"
    print(error_msg)  # Console debug output
    logging.error(error_msg)
    model = None

# Define the features required for prediction
numeric_features = [
    'Carat Weight (ct)', 'Length_mm', 'Width_mm', 'Depth_mm',
    'LW_Ratio', 'DepthPct'
]

categorical_features = [
    'Gem Type', 'Cut/Shape', 'Colour', 'Clarity', 
    'Treatments', 'Certification Status'
]

# Function to get unique values from dataset
def get_unique_values():
    try:
        # Load the dataset
        df = pd.read_csv('../notebooks/data/processed/cleaned_gems.csv')
        
        # Initialize the standardizer
        standardizer = GemStandardizer()
        
        # Filter out 'Not Specified' treatments
        df_filtered = df[df['Treatments'] != 'Not Specified'].copy()
        
        # Get filtered gem types (200+ records, grouped)
        gem_type_options = standardizer.get_filtered_gem_types_from_dataset(df_filtered)
        
        # Get color options - use basic colors only for selection
        color_options = standardizer.get_color_options()
        
        # Get actual values from dataset, filtered and cleaned
        actual_cut_shapes = sorted([x for x in df_filtered['Cut/Shape'].unique().tolist() 
                                  if str(x).strip() and str(x).lower() != 'nan' and x != 'Cut/Shape'])
        
        # Get all unique colors from dataset (for the combined color field)
        actual_colors = sorted([x for x in df_filtered['Colour'].unique().tolist() 
                              if str(x).strip() and str(x).lower() != 'nan' and x != 'Colour'])
        
        actual_clarity = sorted([x for x in df_filtered['Clarity'].unique().tolist() 
                               if str(x).strip() and str(x).lower() != 'nan' and x != 'Clarity'])
        
        actual_treatments = sorted([x for x in df_filtered['Treatments'].unique().tolist() 
                                  if str(x).strip() and str(x).lower() != 'nan' and x != 'Treatments'])
        
        # Build final options
        valid_options = {
            'Gem Type': sorted(list(gem_type_options.keys())),  # Filtered base types (200+ records)
            'Gem Variety': [var for vars in gem_type_options.values() for var in vars],  # Varieties from filtered types
            'Cut/Shape': actual_cut_shapes,  # All cut/shapes from data
            'Color': sorted(list(color_options['colors'])),  # Basic colors only for selection dropdown
            'Tone': color_options['tones'],  # Standard tones for color building
            'Color Modifier': color_options['modifiers'],  # Standard modifiers for color building  
            'Clarity': actual_clarity,  # All clarity grades from data
            'Treatments': actual_treatments,  # All treatments from data (excluding 'Not Specified')
            'Certification': ['Yes', 'No']  # Simple Yes/No for certification
        }
        
        return valid_options
    except Exception as e:
        print(f"Error loading options from dataset: {str(e)}")
        # Fallback to standardizer defaults
        standardizer = GemStandardizer()
        color_options = standardizer.get_color_options()
        gem_type_options = standardizer.get_gem_type_options()
        
        return {
            'Gem Type': sorted(list(gem_type_options.keys())),
            'Gem Variety': [var for vars in gem_type_options.values() for var in vars],
            'Cut/Shape': ['Mixed Brilliant Oval', 'Mixed Brilliant Cushion', 'Asscher Asscher - Octagon', 'Step Cut Fancy', 'Mixed Brilliant Heart'],
            'Color': sorted(list(color_options['colors'])),  # Basic colors only
            'Tone': color_options['tones'],
            'Color Modifier': color_options['modifiers'],
            'Clarity': ['Eye Clean', 'VVS', 'VS', 'SI', 'I'],
            'Treatments': ['Heat Treated', 'No Enhancement'],
            'Certification': ['Yes', 'No']
        }

# Load options when app starts
valid_options = get_unique_values()

def validate_input(data):
    errors = []
    print("Validating input data:", data)  # Debug print
    
    # Validate numeric features
    try:
        carat = float(data.get('carat_weight', 0))
        if not (0.1 <= carat <= 50.0):
            errors.append("Carat weight must be between 0.1 and 50.0")
    except ValueError:
        errors.append("Invalid carat weight value")
        
    for dim in ['length', 'width', 'depth']:
        try:
            value = float(data.get(dim, 0))
            if not (0.5 <= value <= 30.0):
                errors.append(f"{dim.capitalize()} must be between 0.5 and 30.0 mm")
        except ValueError:
            errors.append(f"Invalid {dim} value")
    
    # Validate categorical features
    gem_type = data.get('gem_type', '')
    gem_variety = data.get('gem_variety', '')
    
    if not gem_type or gem_type not in valid_options['Gem Type']:
        errors.append("Invalid gem type selection")
    if gem_variety and gem_variety not in valid_options['Gem Variety']:
        errors.append("Invalid gem variety selection")
    
    # Validate color components
    color = data.get('color', '')
    tone = data.get('tone', '')
    color_modifier = data.get('color_modifier', '')
    
    if not color or color not in valid_options['Color']:
        errors.append("Invalid color selection")
    if tone and tone not in valid_options['Tone']:
        errors.append("Invalid tone selection")
    if color_modifier and color_modifier not in valid_options['Color Modifier']:
        errors.append("Invalid color modifier selection")
        
    # Validate other categorical features
    if data.get('cut_shape') not in valid_options['Cut/Shape']:
        errors.append("Invalid cut/shape selection")
    if data.get('clarity') not in valid_options['Clarity']:
        errors.append("Invalid clarity selection")
    if data.get('treatments') not in valid_options['Treatments']:
        errors.append("Invalid treatment selection")
    if data.get('certification') not in valid_options['Certification']:
        errors.append("Invalid certification selection")
    
    return errors

@app.route('/api/options', methods=['GET'])
def get_options():
    """API endpoint to get all valid options for dropdowns"""
    return jsonify(valid_options)

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for making predictions"""
    prediction = None
    errors = []
    input_summary = None
    session_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    try:
        # Log incoming request
        logger.info(
            f"Received prediction request",
            extra={
                'session_id': session_id,
                'request_data': request.json
            }
        )
        
        # Validate input
        errors = validate_input(request.json)
        if errors:
            log_prediction(session_id, request.json, error=errors)
            return jsonify({'success': False, 'errors': errors})
        
        # Create standardizer instance
        standardizer = GemStandardizer()
        
        # Get gem type and variety
        base_type = request.json['gem_type']
        variety = request.json.get('gem_variety', '')
        gem_type = variety if variety else base_type
        
        # Standardize color components
        color_parts = {
            'tone': request.json.get('tone', ''),
            'color': request.json['color'],
            'modifier': request.json.get('color_modifier', '')
        }
        
        # Combine color components into full color string
        color_str = ' '.join(filter(None, [
            color_parts['tone'],
            color_parts['modifier'],
            color_parts['color']
        ]))
        
        # Prepare input data for prediction
        try:
            input_data = {
                'Carat Weight (ct)': float(request.json['carat_weight']),
                'Length_mm': float(request.json['length']),
                'Width_mm': float(request.json['width']),
                'Depth_mm': float(request.json['depth']),
                'Gem Type': gem_type,
                'Cut/Shape': request.json['cut_shape'],
                'Colour': color_str,
                'Clarity': request.json['clarity'],
                'Treatments': request.json['treatments'],
                'Certification Status': request.json['certification']
            }
        except (KeyError, ValueError) as e:
            error_msg = f"Error processing input data: {str(e)}"
            logger.error(error_msg, extra={'session_id': session_id})
            return jsonify({'success': False, 'errors': [error_msg]})
            
        # Calculate derived features
        input_data['LW_Ratio'] = input_data['Length_mm'] / input_data['Width_mm']
        input_data['DepthPct'] = input_data['Depth_mm'] / ((input_data['Length_mm'] + input_data['Width_mm']) / 2) * 100
        
        if model is not None:
            # Create DataFrame
            X = pd.DataFrame([input_data])
            
            # Make prediction
            raw_prediction = model.predict(X)
            final_prediction = np.expm1(raw_prediction)[0]  # Convert back from log scale
            
            # Format prediction as currency
            prediction = f"LKR {final_prediction:,.2f}"
            
            # Create input summary
            input_summary = {
                'Gem Type': input_data['Gem Type'],
                'Carat': f"{input_data['Carat Weight (ct)']:.2f} ct",
                'Dimensions': f"{input_data['Length_mm']:.1f} x {input_data['Width_mm']:.1f} x {input_data['Depth_mm']:.1f} mm",
                'Color': input_data['Colour'],
                'Clarity': input_data['Clarity'],
                'Treatment': input_data['Treatments']
            }
            
            # Log successful prediction
            processing_time = (datetime.now() - start_time).total_seconds()
            log_data = {
                'input_data': input_data,
                'prediction_value': final_prediction,
                'formatted_prediction': prediction,
                'processing_time_seconds': processing_time
            }
            logger.info(
                f"Successful prediction completed in {processing_time:.2f}s",
                extra={
                    'session_id': session_id,
                    'prediction_data': log_data
                }
            )
            
            return jsonify({
                'success': True,
                'prediction': prediction,
                'input_summary': input_summary
            })
        else:
            error_msg = 'Model not loaded. Please check server logs.'
            log_prediction(session_id, input_data, error=error_msg)
            return jsonify({
                'success': False,
                'errors': [error_msg]
            })

    except Exception as e:
        error_msg = f"Error during prediction: {str(e)}"
        log_prediction(session_id, request.json, error=error_msg)
        return jsonify({'success': False, 'errors': [error_msg]})

@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    errors = []
    input_summary = None
    session_id = str(uuid.uuid4())
    start_time = datetime.now()

    if request.method == 'POST':
        logger.info(
            "Received POST request",
            extra={
                'session_id': session_id,
                'request_type': 'web_form'
            }
        )
        
        try:
            # Log form data
            form_data = dict(request.form)
            logger.info(
                "Processing form submission",
                extra={
                    'session_id': session_id,
                    'form_data': form_data
                }
            )
            
            # Validate input
            errors = validate_input(form_data)
            if errors:
                log_prediction(session_id, form_data, error=errors)
            
            if not errors:
                logger.info(
                    "Form validation passed, processing input...",
                    extra={'session_id': session_id}
                )
                
                try:
                    # Get gem type and variety
                    base_type = form_data['gem_type']
                    variety = form_data.get('gem_variety', '')
                    gem_type = variety if variety else base_type
                    
                    # Combine color components into full color string
                    color_parts = {
                        'tone': form_data.get('tone', ''),
                        'color': form_data.get('color', ''),
                        'modifier': form_data.get('color_modifier', '')
                    }
                    
                    # Combine color components into full color string
                    color_str = ' '.join(filter(None, [
                        color_parts['tone'],
                        color_parts['modifier'],
                        color_parts['color']
                    ]))
                    
                    # Process form data
                    input_data = {
                        'Carat Weight (ct)': float(form_data['carat_weight']),
                        'Length_mm': float(form_data['length']),
                        'Width_mm': float(form_data['width']),
                        'Depth_mm': float(form_data['depth']),
                        'Gem Type': gem_type,
                        'Cut/Shape': form_data['cut_shape'],
                        'Colour': color_str,
                        'Clarity': form_data['clarity'],
                        'Treatments': form_data['treatments'],
                        'Certification Status': form_data['certification']
                    }
                    
                    # Calculate derived features
                    input_data['LW_Ratio'] = input_data['Length_mm'] / input_data['Width_mm']
                    input_data['DepthPct'] = input_data['Depth_mm'] / ((input_data['Length_mm'] + input_data['Width_mm']) / 2) * 100
                    
                    logger.info(
                        "Processed input data",
                        extra={
                            'session_id': session_id,
                            'processed_data': input_data
                        }
                    )

                    if model is not None:
                        # Create DataFrame
                        X = pd.DataFrame([input_data])
                        
                        # Make prediction
                        raw_prediction = model.predict(X)
                        final_prediction = np.expm1(raw_prediction)[0]  # Convert back from log scale
                        
                        # Format prediction as currency
                        prediction = f"LKR {final_prediction:,.2f}"
                        
                        # Create input summary for display
                        input_summary = {
                            'Gem Type': input_data['Gem Type'],
                            'Carat': f"{input_data['Carat Weight (ct)']:.2f} ct",
                            'Dimensions': f"{input_data['Length_mm']:.1f} x {input_data['Width_mm']:.1f} x {input_data['Depth_mm']:.1f} mm",
                            'Color': input_data['Colour'],
                            'Clarity': input_data['Clarity'],
                            'Treatment': input_data['Treatments']
                        }

                        # Log successful prediction
                        processing_time = (datetime.now() - start_time).total_seconds()
                        log_data = {
                            'input_data': input_data,
                            'prediction_value': final_prediction,
                            'formatted_prediction': prediction,
                            'processing_time_seconds': processing_time
                        }
                        logger.info(
                            f"Successful web form prediction completed in {processing_time:.2f}s",
                            extra={
                                'session_id': session_id,
                                'prediction_data': log_data
                            }
                        )
                    else:
                        error_msg = "Model not loaded. Please check server logs."
                        logger.error(
                            error_msg,
                            extra={
                                'session_id': session_id,
                                'error_type': 'model_not_loaded'
                            }
                        )
                        errors.append(error_msg)

                except KeyError as e:
                    error_msg = f"Missing form field: {str(e)}"
                    log_prediction(session_id, form_data, error=error_msg)
                    errors.append(error_msg)
                except ValueError as e:
                    error_msg = f"Invalid numeric value: {str(e)}"
                    log_prediction(session_id, form_data, error=error_msg)
                    errors.append(error_msg)
                except Exception as e:
                    error_msg = f"Error during prediction: {str(e)}"
                    log_prediction(session_id, form_data, error=error_msg)
                    errors.append(error_msg)

        except Exception as e:
            error_msg = f"Server error: {str(e)}"
            log_prediction(session_id, request.form if hasattr(request, 'form') else None, error=error_msg)
            errors.append(error_msg)

    return render_template('index.html', 
                         prediction=prediction, 
                         errors=errors,
                         input_summary=input_summary,
                         valid_options=valid_options)

if __name__ == '__main__':
    print("\n💎 Starting Gem Price Prediction System...")
    print("----------------------------------------")
    print("Access the application at: http://127.0.0.1:5001")
    print("Press CTRL+C to quit")
    print("----------------------------------------\n")
    app.run(debug=True, host='127.0.0.1', port=5001)
