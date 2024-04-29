# app.py
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from extensions import db
from flask import request, jsonify, abort
from models import db, Model, Dataset, Version, Server, ModelDeployment
from sqlalchemy import and_,text, create_engine
import sqlite3


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database1.db'

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], isolation_level="SERIALIZABLE")
db.init_app(app) # Initialize db with the Flask app
#engine.execute('CREATE PROCEDURE my_procedure(IN param1 INT, IN param2 INT) AS BEGIN END;')

migrate = Migrate(app, db)

from models import Model, Dataset, Version, Server, ModelDeployment

@app.route('/test')
def test():
    return 'successful'

@app.route('/')
def index():
    return 'Welcome to the Machine Learning Model Management API!'

# Create a Model
@app.route('/models', methods=['POST'])
def create_model():
    data = request.get_json()
    new_model = Model(name=data['name'], description=data['description'], type=data['type'])
    db.session.add(new_model)
    db.session.commit()
    return jsonify(new_model.id), 201

# Read all Models
@app.route('/models', methods=['GET'])
def get_models():
    models = Model.query.all()
    models_data = [
    {'id': model.id, 'name': model.name, 'description': model.description, 'type': model.type}
    for model in models
    ]
    return jsonify(models_data), 200

@app.route('/models/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    model = Model.query.get(model_id)
    if model is None:
        abort(404)
    data = request.get_json()
    model.name = data['name']
    model.description = data['description']
    model.type = data['type']
    db.session.commit()
    return jsonify({'message': 'Model updated'}), 200

@app.route('/datasets/<int:dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        abort(404)
    data = request.get_json()
    dataset.name = data['name']
    dataset.description = data['description']
    dataset.data_type = data['data_type']
    db.session.commit()
    return jsonify({'message': 'Dataset updated'}), 200


@app.route('/versions/<int:version_id>', methods=['PUT'])
def update_version(version_id):
    version = Version.query.get(version_id)
    if not version:
        abort(404)
    data = request.get_json()
    version.model_id = data['model_id']
    version.dataset_id = data['dataset_id']
    version.version_number = data['version_number']
    version.performance_metrics = data['performance_metrics']
    db.session.commit()
    return jsonify({'message': 'Version updated'}), 200

@app.route('/modeldeployments/<int:deployment_id>', methods=['PUT'])
def update_model_deployment(deployment_id):
    deployment = ModelDeployment.query.get(deployment_id)
    if not deployment:
        abort(404)
    data = request.get_json()
    deployment.server_id = data['server_id']
    deployment.version_id = data['version_id']
    deployment.deployment_time = datetime.fromisoformat(data['deployment_time'])
    db.session.commit()
    return jsonify({'message': 'Deployment updated'}), 200



# Delete a Model
@app.route('/models/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    model = Model.query.get(model_id)
    if model is None:
        abort(404)
    db.session.delete(model)
    db.session.commit()
    return jsonify({'message': 'Model deleted'}), 200

# Create and Read operations for Dataset
@app.route('/datasets', methods=['GET', 'POST'])
def handle_datasets():
    if request.method == 'POST':
        data = request.get_json()
        new_dataset = Dataset(name=data['name'], description=data['description'], data_type=data['data_type'])
        db.session.add(new_dataset)
        db.session.commit()
        return jsonify(new_dataset.id), 201
    else:
        datasets = Dataset.query.all()
        datasets_data = [{'id': dataset.id, 'name': dataset.name, 'description': dataset.description, 'data_type': dataset.data_type} for dataset in datasets]
        return jsonify(datasets_data), 200

# Create and Read operations for Version
@app.route('/versions', methods=['GET', 'POST'])
def handle_versions():
    if request.method == 'POST':
        data = request.get_json()
        new_version = Version(model_id=data['model_id'], dataset_id=data['dataset_id'], version_number=data['version_number'], performance_metrics=data['performance_metrics'])
        db.session.add(new_version)
        db.session.commit()
        return jsonify(new_version.id), 201
    else:
        versions = Version.query.all()
        versions_data = [{'id': version.id, 'model_id': version.model_id, 'dataset_id': version.dataset_id, 'version_number': version.version_number, 'performance_metrics': version.performance_metrics} for version in versions]
        return jsonify(versions_data), 200

# Create and Read operations for Server
@app.route('/servers', methods=['GET', 'POST'])
def handle_servers():
    if request.method == 'POST':
        data = request.get_json()
        new_server = Server(name=data['name'], ip_address=data['ip_address'])
        db.session.add(new_server)
        db.session.commit()
        return jsonify(new_server.id), 201
    else:
        servers = Server.query.all()
        servers_data = [{'id': server.id, 'name': server.name, 'ip_address': server.ip_address} for server in servers]
        return jsonify(servers_data), 200

@app.route('/servers/<int:server_id>', methods=['PUT'])
def update_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        abort(404)
    data = request.get_json()
    server.name = data['name']
    server.ip_address = data['ip_address']
    db.session.commit()
    return jsonify({'message': 'Server updated'}), 200


@app.route('/modeldeployments', methods=['GET', 'POST'])
def handle_modeldeployments():
    if request.method == 'POST':
        data = request.get_json()
        # Directly use the integer value for deployment_time without converting from datetime
        deployment_time = data.get('deployment_time', None) # Expecting MMDD as an integer
        if not deployment_time:
            return jsonify({'error': 'deployment_time is required'}), 400
        new_deployment = ModelDeployment(
        server_id=data['server_id'],
        version_id=data['version_id'],
        deployment_time=deployment_time # Stored as an integer
        )
        db.session.add(new_deployment)
        db.session.commit()
        return jsonify(new_deployment.id), 201
    else:
        deployments = ModelDeployment.query.all()
        deployments_data = [{
        'id': deployment.id,
        'server_id': deployment.server_id,
        'version_id': deployment.version_id,
        'deployment_time': deployment.deployment_time # No conversion needed, directly use the integer
        } for deployment in deployments]
        return jsonify(deployments_data), 200



@app.route('/datasets/<int:dataset_id>', methods=['PUT', 'DELETE'])
def handle_dataset(dataset_id):
    dataset = Dataset.query.get(dataset_id)
    if not dataset:
        abort(404, description="Resource not found")
    if request.method == 'PUT':
        data = request.get_json()
        dataset.name = data['name']
        dataset.description = data['description']
        dataset.data_type = data['data_type']
        db.session.commit()
        return jsonify({'message': 'Dataset updated'}), 200

    elif request.method == 'DELETE':
        db.session.delete(dataset)
        db.session.commit()
        return jsonify({'message': 'Dataset deleted'}), 200

# Update and Delete operations for Version
@app.route('/versions/<int:version_id>', methods=['PUT', 'DELETE'])
def handle_version(version_id):
    version = Version.query.get(version_id)
    if not version:
        abort(404, description="Resource not found")
    if request.method == 'PUT':
        data = request.get_json()
        version.model_id = data['model_id']
        version.dataset_id = data['dataset_id']
        version.version_number = data['version_number']
        version.performance_metrics = data['performance_metrics']
        db.session.commit()
        return jsonify({'message': 'Version updated'}), 200
    elif request.method == 'DELETE':
        db.session.delete(version)
        db.session.commit()
        return jsonify({'message': 'Version deleted'}), 200


# Update and Delete operations for Server
@app.route('/servers/<int:server_id>', methods=['PUT', 'DELETE'])
def handle_server(server_id):
    server = Server.query.get(server_id)
    if not server:
        abort(404, description="Resource not found")
    if request.method == 'PUT':
        data = request.get_json()
        server.name = data['name']
        server.ip_address = data['ip_address']
        db.session.commit()
        return jsonify({'message': 'Server updated'}), 200

    elif request.method == 'DELETE':
        db.session.delete(server)
        db.session.commit()
        return jsonify({'message': 'Server deleted'}), 200

# Update and Delete operations for ModelDeployment
@app.route('/modeldeployments/<int:deployment_id>', methods=['PUT', 'DELETE'])
def handle_model_deployment(deployment_id):
    deployment = ModelDeployment.query.get(deployment_id)
    if not deployment:
        abort(404, description="Resource not found")
    if request.method == 'PUT':
        data = request.get_json()
        deployment.server_id = data['server_id']
        deployment.version_id = data['version_id']
        # Note: deployment_time should be a datetime object, you may need to parse it from the string
        deployment.deployment_time = datetime.fromisoformat(data['deployment_time'])
        db.session.commit()
        return jsonify({'message': 'Deployment updated'}), 200

    elif request.method == 'DELETE':
        db.session.delete(deployment)
        db.session.commit()
        return jsonify({'message': 'Deployment deleted'}), 200


@app.route('/models/count/<model_type>', methods=['GET'])
def count_models_by_type(model_type):
    # Calling a stored procedure
    result = db.session.execute(func.CountModelsByType(model_type))
    models_count = result.scalar()
    return jsonify({'model_type': model_type, 'count': models_count}), 200

@app.route('/models/type/<model_type>', methods=['GET'])
def get_models_by_type(model_type):
    stmt = db.text("SELECT * FROM model WHERE type = :model_type")
    result = db.engine.execute(stmt, model_type=model_type)
    models = [{'id': row[0], 'name': row[1], 'description': row[2], 'type': row[3]} for row in result]
    return jsonify(models)


@app.route('/reports/deployments', methods=['GET'])
def generate_deployment_report():
    #db.session.execute(text('CREATE PROCEDURE my_procedure(IN param1 INT, IN param2 INT) AS BEGIN END;'))
    start_date = request.args.get('start_date', type=int)
    end_date = request.args.get('end_date', type=int)
    model_type = request.args.get('model_type', default=None, type=str)

    # Building SQL dynamically based on input

    input_text = ''''''

    params = {'start_date': start_date, 'end_date': end_date}
    if model_type and model_type != "All":
        input_text = ' AND m.type = :model_type'
        params['model_type'] = model_type

    #input_text = "SELECT md.id, s.name AS server_name, m.name AS model_name, md.deployment_time FROM model_deployment md JOIN version v ON md.version_id = v.id JOIN model m ON v.model_id = m.id JOIN server s ON md.server_id = s.id WHERE md.deployment_time BETWEEN :start_date AND :end_date" + input_text
    input_text = "SELECT md.id, s.name AS server_name, m.name AS model_name, md.deployment_time FROM model_deployment md JOIN version v ON md.version_id = v.id JOIN model m ON v.model_id = m.id JOIN server s ON md.server_id = s.id WHERE md.deployment_time BETWEEN :start_date AND :end_date" + input_text

    #db.Prepare()
    print(input_text)
    sql = text(input_text)
    result = db.session.execute(sql, params).fetchall()
    #result = db.session.execute(sql).fetchall()
    deployments = [{
        'id': row.id, 
        'server_name': row.server_name, 
        'model_name': row.model_name, 
        'deployment_time': row.deployment_time
    } for row in result]
    print("dep: ", jsonify(deployments)) 
    return jsonify(deployments)



@app.route('/reports/top-servers', methods=['GET'])
def get_top_servers():
    top_x = request.args.get('top', default=5, type=int)  # Get the 'top' parameter from the query string, default to 5

    # Build SQL query dynamically based on input
    input_text = "SELECT s.id AS server_id, s.name AS server_name, COUNT(md.id) AS deployment_count FROM server s JOIN model_deployment md ON s.id = md.server_id GROUP BY s.id, s.name ORDER BY COUNT(md.id) DESC LIMIT :top_x"

    params = {'top_x': top_x}

    # Debugging: Print the final SQL query to check
    print(input_text)

    # Execute the SQL query
    sql = text(input_text)
    result = db.session.execute(sql, params).fetchall()

    # Build a list of dictionaries to hold the result for JSON conversion
    top_servers = [{
        'server_id': row.server_id,
        'server_name': row.server_name,
        'deployment_count': row.deployment_count
    } for row in result]

    # Debugging: Print the JSON output to check
    print("Top Servers: ", jsonify(top_servers))

    return jsonify(top_servers)


@app.route('/reports/model-types-count', methods=['GET'])
def get_model_types_count():
    # Build SQL query dynamically based on input
    input_text = """
    SELECT m.type AS model_type, COUNT(md.id) AS deployment_count
    FROM model m
    JOIN version v ON m.id = v.model_id
    JOIN model_deployment md ON v.id = md.version_id
    GROUP BY m.type
    ORDER BY COUNT(md.id) DESC
    """

    # Debugging: Print the final SQL query to check
    print(input_text)

    # Execute the SQL query
    sql = text(input_text)
    result = db.session.execute(sql)

    # Convert result set to dictionary format
    model_types_count = [{
        'model_type': row.model_type,
        'deployment_count': row.deployment_count
    } for row in result]

    # Debugging: Print the JSON output to check
    print("Model Types Count: ", jsonify(model_types_count))

    return jsonify(model_types_count)

@app.route('/reports/top-datasets', methods=['GET'])
def get_top_datasets():
    top_x = request.args.get('top', default=5, type=int)  # Get the 'top' parameter from the query string, default to 5

    # Build SQL query dynamically based on input
    input_text = """
    SELECT d.id AS dataset_id, d.name AS dataset_name, COUNT(v.id) AS version_count
    FROM dataset d
    JOIN version v ON d.id = v.dataset_id
    GROUP BY d.id, d.name
    ORDER BY COUNT(v.id) DESC
    LIMIT :top_x
    """

    params = {'top_x': top_x}

    # Debugging: Print the final SQL query to check
    print(input_text)

    # Execute the SQL query
    sql = text(input_text)
    result = db.session.execute(sql, params).fetchall()

    # Build a list of dictionaries to hold the result for JSON conversion
    top_datasets = [{
        'dataset_id': row.dataset_id,
        'dataset_name': row.dataset_name,
        'version_count': row.version_count
    } for row in result]

    # Debugging: Print the JSON output to check
    print("Top Datasets: ", jsonify(top_datasets))

    return jsonify(top_datasets)

@app.route('/datasets/list', methods=['GET'])
def list_datasets():
    query = "SELECT id, name FROM dataset ORDER BY name"
    result = db.session.execute(text(query))
    datasets = [{'dataset_id': row.id, 'dataset_name': row.name} for row in result]
    return jsonify(datasets)

@app.route('/models/by-dataset', methods=['GET'])
def models_by_dataset():
    dataset_id = request.args.get('dataset_id', type=int)

    query = """
    SELECT m.id AS model_id, m.name AS model_name, m.description, COUNT(md.id) AS deployment_count
    FROM model m
    JOIN version v ON m.id = v.model_id
    JOIN model_deployment md ON v.id = md.version_id
    WHERE v.dataset_id = :dataset_id
    GROUP BY m.id
    """

    params = {'dataset_id': dataset_id}
    result = db.session.execute(text(query), params)
    models = [{
        'model_id': row.model_id,
        'model_name': row.model_name,
        'model_description': row.description,
        'deployment_count': row.deployment_count
    } for row in result]

    return jsonify(models)



@app.route('/reports/top-models', methods=['GET'])
def get_top_models():
    top_x = request.args.get('top', default=5, type=int)  # Get the 'top' parameter from the query string, default to 5

    # Build SQL query dynamically based on input
    input_text = """
    SELECT m.id AS model_id, m.name AS model_name, COUNT(md.id) AS deployment_count
    FROM model m
    JOIN version v ON m.id = v.model_id
    JOIN model_deployment md ON v.id = md.version_id
    GROUP BY m.id, m.name
    ORDER BY COUNT(md.id) DESC
    LIMIT :top_x
    """

    params = {'top_x': top_x}

    # Debugging: Print the final SQL query to check
    print(input_text)

    # Execute the SQL query
    sql = text(input_text)
    result = db.session.execute(sql, params).fetchall()

    # Build a list of dictionaries to hold the result for JSON conversion
    top_models = [{
        'model_id': row.model_id,
        'model_name': row.model_name,
        'deployment_count': row.deployment_count
    } for row in result]

    # Debugging: Print the JSON output to check
    print("Top Models: ", jsonify(top_models))

    return jsonify(top_models)


from sqlalchemy import text
from sqlalchemy import func



@app.route('/reports/server-deployments', methods=['GET'])
def server_deployment_report():
    start_date = request.args.get('start_date', type=int)
    end_date = request.args.get('end_date', type=int)
    model_type = request.args.get('model_type', default=None, type=str)

    # SQL query dynamically built based on input
    query_parts = [
        "SELECT s.id AS server_id, s.name AS server_name, COUNT(md.id) AS deployment_count",
        "FROM server s",
        "JOIN model_deployment md ON s.id = md.server_id",
        "JOIN version v ON md.version_id = v.id",
        "JOIN model m ON v.model_id = m.id",
        "WHERE md.deployment_time BETWEEN :start_date AND :end_date"
    ]

    params = {'start_date': start_date, 'end_date': end_date}
    
    if model_type and model_type != "All":
        query_parts.append("AND m.type = :model_type")
        params['model_type'] = model_type
    
    query_parts.append("GROUP BY s.id, s.name")
    
    input_text = " ".join(query_parts)

    # Execute the SQL query
    sql = text(input_text)
    result = db.session.execute(sql, params).fetchall()
    
    # Build result JSON
    deployments = [{
        'server_id': row.server_id,
        'server_name': row.server_name,
        'deployment_count': row.deployment_count
    } for row in result]

    return jsonify(deployments)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)