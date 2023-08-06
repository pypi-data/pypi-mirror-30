import NodeDefender
from flask_sqlalchemy import SQLAlchemy
import logging

SQL = SQLAlchemy()

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

def load(app, loggHandler = None):
    if loggHandler:
        logger.addHandler(loggHandler)
    SQL.app = app
    with app.app_context():
        SQL.init_app(app)
    if app.config['SQLALCHEMY_DATABASE_URI'] == "sqlite:///:memory:":
        NodeDefender.db.sql.logger.warning("Database URI not valid, using RAM as SQL")
        SQL.create_all()
    NodeDefender.db.sql.logger.info("SQL Initialized")
    return SQL

from NodeDefender.db.sql.group import GroupModel
from NodeDefender.db.sql.user import UserModel
from NodeDefender.db.sql.node import NodeModel, LocationModel
from NodeDefender.db.sql.icpe import iCPEModel, SensorModel,\
        CommandClassModel, CommandClassTypeModel
from NodeDefender.db.sql.data import PowerModel, HeatModel, EventModel
from NodeDefender.db.sql.conn import MQTTModel
from NodeDefender.db.sql.message import MessageModel
