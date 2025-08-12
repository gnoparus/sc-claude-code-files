"""
Simple logging configuration for the E-commerce Analytics Dashboard.
"""

import os
from pathlib import Path
from loguru import logger
import streamlit as st
from datetime import datetime

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

def setup_simple_logging():
    """Set up simple file and console logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler - colored output
    logger.add(
        sink=lambda msg: print(msg, end=""),  # Direct to stdout
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}:{function}</cyan> | {message}",
        colorize=True
    )
    
    # File handler - simple format
    logger.add(
        sink=LOGS_DIR / "dashboard.log",
        level="DEBUG", 
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        rotation="1 day",
        retention="7 days",
        compression="zip"
    )
    
    # Error-only file
    logger.add(
        sink=LOGS_DIR / "errors.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days"
    )
    
    logger.info("Simple logging system initialized")

# Initialize logging when imported
setup_simple_logging()