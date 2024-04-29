from sqlalchemy import Index
from app import db  # Assuming 'app' is the correct import for db, remove 'from extensions import db' if not used
from sqlalchemy.orm import relationship

class Model(db.Model):
    __tablename__ = 'model'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    versions = relationship('Version', backref='model', lazy=True)
    type = db.Column(db.String(50), nullable=False, index=True)  # Indexing on model type for faster access on type-based queries

    __table_args__ = (
        Index('idx_model_type_id', 'type', 'id'),  # Composite index for filtering on type and sorting/joining on id
    )

class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Indexing on dataset name for alphabetical sorting and quick lookup
    description = db.Column(db.Text, nullable=True)
    data_type = db.Column(db.String(50), nullable=False)
    versions = relationship('Version', backref='dataset', lazy=True)

class Version(db.Model):
    __tablename__ = 'version'
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=False)
    version_number = db.Column(db.String(50), nullable=False)
    performance_metrics = db.Column(db.Text, nullable=True)

    __table_args__ = (
        Index('idx_version_model_dataset', 'model_id', 'dataset_id'),  # Composite index for efficient joins and filtering on model and dataset
    )

class Server(db.Model):
    __tablename__ = 'server'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # Indexing server name for quick lookups
    ip_address = db.Column(db.String(15), nullable=False)  # IPv4 address format, consider if indexing is needed based on query patterns
    model_versions = relationship('ModelDeployment', backref='server', lazy=True)

class ModelDeployment(db.Model):
    __tablename__ = 'model_deployment'
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    version_id = db.Column(db.Integer, db.ForeignKey('version.id'), nullable=False)
    deployment_time = db.Column(db.Integer, nullable=False, index=True)  # Indexing deployment time for filtering by date ranges

    __table_args__ = (
        Index('idx_deployment_server_time', 'server_id', 'deployment_time'),  # Composite index to optimize queries filtering by server and time range
    )
