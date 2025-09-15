import logging
import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Check if running in Azure Container App
RUNNING_IN_AZURE = os.environ.get('WEBSITE_SITE_NAME') is not None

class StructuredLogFormatter(logging.Formatter):
    """
    Formatter for structured logging in JSON format.
    Includes correlation ID and additional context data.
    """
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add correlation ID if available
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add custom fields if available
        if hasattr(record, 'custom_fields') and record.custom_fields:
            for key, value in record.custom_fields.items():
                log_data[key] = value
        
        return json.dumps(log_data)

class CorrelationAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds correlation ID to all log records.
    Useful for tracking requests across services.
    """
    
    def __init__(self, logger, correlation_id=None):
        super().__init__(logger, {})
        self.correlation_id = correlation_id or str(uuid.uuid4())
    
    def process(self, msg, kwargs):
        # Create copy of kwargs to avoid modifying the original
        kwargs_copy = kwargs.copy()
        
        # Add extra dict if not present
        if 'extra' not in kwargs_copy:
            kwargs_copy['extra'] = {}
        
        # Add correlation ID to extra
        kwargs_copy['extra']['correlation_id'] = self.correlation_id
        
        return msg, kwargs_copy
    
    def with_custom_fields(self, **fields):
        """Add custom fields to the log records."""
        def process(msg, kwargs):
            msg, kwargs = self.process(msg, kwargs)
            
            # Add extra dict if not present
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            
            # Add custom fields to extra
            if 'custom_fields' not in kwargs['extra']:
                kwargs['extra']['custom_fields'] = {}
            
            kwargs['extra']['custom_fields'].update(fields)
            return msg, kwargs
        
        # Create a new adapter with the process method overridden
        adapter = CorrelationAdapter(self.logger, self.correlation_id)
        adapter.process = process
        return adapter

def configure_logging(app_name: str = 'infinityai-backend', log_level: str = 'INFO'):
    """
    Configure structured logging for the application.
    Automatically detects Azure environment and integrates with App Insights.
    """
    # Convert log level string to constant
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler with structured formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredLogFormatter())
    root_logger.addHandler(console_handler)
    
    # Add Application Insights integration if running in Azure
    if RUNNING_IN_AZURE:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            
            # Get connection string from environment
            connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
            if connection_string:
                azure_handler = AzureLogHandler(connection_string=connection_string)
                azure_handler.setFormatter(StructuredLogFormatter())
                root_logger.addHandler(azure_handler)
                root_logger.info(f"Azure Application Insights integration enabled for {app_name}")
        except ImportError:
            root_logger.warning("opencensus-ext-azure package not installed. Azure logging integration disabled.")
    
    # Create and return the base logger for the application
    app_logger = logging.getLogger(app_name)
    return app_logger

def get_logger(module_name: str, correlation_id: Optional[str] = None):
    """
    Get a logger for a specific module with correlation ID support.
    """
    logger = logging.getLogger(f"infinityai-backend.{module_name}")
    return CorrelationAdapter(logger, correlation_id)