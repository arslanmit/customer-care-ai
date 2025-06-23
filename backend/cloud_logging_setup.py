import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

def setup_cloud_logging(project_name, log_name="rasa_chatbot"):
    """
    Sets up Google Cloud Logging for the application
    
    Args:
        project_name: Google Cloud project name
        log_name: Name for the log in Google Cloud
        
    Returns:
        Logger configured for Google Cloud
    """
    try:
        client = google.cloud.logging.Client(project=project_name)
        handler = CloudLoggingHandler(client, name=log_name)
        
        cloud_logger = logging.getLogger('rasa_cloud_logger')
        cloud_logger.setLevel(logging.INFO)
        cloud_logger.addHandler(handler)
        
        cloud_logger.info(f"Google Cloud Logging initialized for {project_name}")
        return cloud_logger
    except Exception as e:
        print(f"Failed to set up Google Cloud Logging: {e}")
        # Fall back to standard logging
        fallback_logger = logging.getLogger('rasa_fallback_logger')
        fallback_logger.setLevel(logging.INFO)
        fallback_logger.addHandler(logging.StreamHandler())
        return fallback_logger
