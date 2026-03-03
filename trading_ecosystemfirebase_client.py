"""
Firebase client for real-time state management and data storage.
Primary database for the trading ecosystem.
"""
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_document import DocumentSnapshot

class FirebaseClient:
    """Firebase Firestore client with error handling and connection management"""
    
    def __init__(self, config):
        self.logger = logging.getLogger(__