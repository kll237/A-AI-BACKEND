import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import asyncio
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class AIEngine:
    """
    The main AI Engine class that orchestrates rule processing and camera streams
    """
    def __init__(self):
        self.rules: Dict[str, Any] = {}  # Store rules by ID
        self.cameras: Dict[str, Any] = {}  # Store camera info by ID
        self.users: Dict[str, Any] = {}  # Store user info by ID
        self.active_processors: Dict[str, Any] = {}  # Store active processors by camera ID
        self.running: bool = False
        from app.services.user_service import UserService
        self.user_service = UserService()  # Create our own instance
        self.attendance_records: Dict[str, Any] = {}  # Format: {date: {user_id: {'entry': time, 'exit': time, 'present': bool}}}
        self.unauthorized_logs: List[Any] = []  # List of unauthorized entry logs
        self.camera_active_status_cache: Dict[str, bool] = {}  # Initialize cache here

        # 修复：使用 PROJECT_ROOT 而不是 BASE_DIR
        try:
            from app.core.config import settings
            self.settings = settings
        except ImportError:
            # 备选导入方式
            import sys
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = Path(current_dir).parent.parent
            sys.path.insert(0, str(project_root))
            from app.core.config import settings
            self.settings = settings
        
        # 使用配置中的路径
        self.project_root = self.settings.PROJECT_ROOT
        self.data_dir = self.settings.DATA_DIR
        self.logs_dir = self.settings.LOGS_DIR
        
        # Create logs directory if it doesn't exist
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Create attendance directory if it doesn't exist
        self.attendance_dir = self.data_dir / "attendance"
        os.makedirs(self.attendance_dir, exist_ok=True)
        
        # Create unauthorized directory if it doesn't exist
        self.unauthorized_dir = self.data_dir / "unauthorized"
        os.makedirs(self.unauthorized_dir, exist_ok=True)
    
        self._load_data()  # Moved _load_data() call to the end of __init__
    
    def _load_data(self):
        """Load rules, cameras, and users data from JSON files"""
        # Load rules
        rules_file = self.data_dir / "rules.json"
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
                logger.info(f"Loaded {len(self.rules)} rules from {rules_file}")
        else:
            logger.warning(f"Rules file not found at {rules_file}")
            # 创建空的rules文件
            with open(rules_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        
        # Load cameras
        cameras_file = self.data_dir / "cameras.json"
        if os.path.exists(cameras_file):
            with open(cameras_file, 'r', encoding='utf-8') as f:
                loaded_cameras = json.load(f)
                for cam_id, cam_data in loaded_cameras.items():
                    self.cameras[cam_id] = cam_data  # Ensure self.cameras is populated
                    self.camera_active_status_cache[cam_id] = cam_data.get("is_active", False)
                logger.info(f"Loaded {len(self.cameras)} cameras from {cameras_file}")
        else:
            self.cameras = {}
            logger.info(f"Cameras file not found at {cameras_file}")
            # 创建空的cameras文件
            with open(cameras_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
        
        # Load users
        users_file = self.data_dir / "users.json"
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
                logger.info(f"Loaded {len(self.users)} users from {users_file}")
        else:
            logger.info(f"Users file not found at {users_file}")
            # 创建空的users文件
            with open(users_file, 'w', encoding='utf-8') as f:
                json.dump({}, f)
    
    def start(self):
        """Start the AI engine processing"""
        if self.running:
            logger.info("AI Engine is already running")
            return
        
        self.running = True
        self._load_data()  # Reload data before starting
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("AI Engine started successfully")
    
    def stop(self):
        """Stop the AI engine processing"""
        if not self.running:
            logger.info("AI Engine is not running")
            return
        
        self.running = False
        
        # Clean up any active processors
        for camera_id, processor in self.active_processors.items():
            try:
                processor.stop()
            except:
                pass
        
        self.active_processors = {}
        logger.info("AI Engine stopped successfully")
    
    def _monitor_loop(self):
        """Monitor loop to process rules, camera streams, and update active status."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            while self.running:
                # Check and update camera active statuses
                try:
                    loop.run_until_complete(self._check_camera_streams_async())
                except Exception as e:
                    logger.error(f"Error checking camera streams: {str(e)}")
                
                self._process_rules()  # This remains synchronous for now
                self._initialize_filter_processors()  # This remains synchronous
                
                # 使用配置中的间隔或默认值
                monitor_interval = getattr(self.settings, 'AI_ENGINE_MONITOR_INTERVAL_SECONDS', 5)
                time.sleep(monitor_interval)
        except Exception as e:
            logger.error(f"Error in monitor loop: {str(e)}", exc_info=True)
            self.running = False
        finally:
            loop.close()
    
    async def _check_camera_streams_async(self):
        """Periodically checks all camera streams and updates their active status."""
        logger.debug("Checking camera stream statuses...")
        # Create a temporary copy of camera IDs to iterate over, in case self.cameras is modified elsewhere
        current_camera_ids = list(self.cameras.keys())

        for camera_id in current_camera_ids:
            camera_data = self.cameras.get(camera_id)
            if not camera_data or not camera_data.get("rtsp_url"):
                logger.debug(f"Camera {camera_id} has no data or RTSP URL, skipping status check.")
                continue

            rtsp_url = camera_data["rtsp_url"]
            is_currently_active = False  # Assume inactive until proven active
            try:
                # Try to import StreamValidator
                try:
                    from app.utils.stream_validator import StreamValidator
                    # Use StreamValidator to check stream
                    validation_result = await asyncio.to_thread(StreamValidator.validate_rtsp_stream, rtsp_url)
                    is_currently_active = validation_result.get("is_valid", False)
                    logger.debug(f"Camera {camera_id} ({rtsp_url}) validation: {validation_result}")
                except ImportError:
                    logger.warning(f"StreamValidator not available, skipping stream check for camera {camera_id}")
                    continue

            except Exception as e:
                logger.error(f"Error validating stream for camera {camera_id} ({rtsp_url}): {e}")
                is_currently_active = False

            # Update status if it has changed from the cached status
            previous_status = self.camera_active_status_cache.get(camera_id, False)
            if is_currently_active != previous_status:
                logger.info(f"Camera {camera_id} status changed: {previous_status} -> {is_currently_active}")
                
                # Try to update via camera service
                try:
                    from app.services.camera_service import camera_service
                    updated_camera = await camera_service.update_camera_active_status(camera_id, is_currently_active)
                    if updated_camera:
                        self.camera_active_status_cache[camera_id] = updated_camera.is_active
                        # Update self.cameras entry as well to keep it in sync with the persisted data
                        self.cameras[camera_id]["is_active"] = updated_camera.is_active
                    else:
                        logger.warning(f"Failed to update active status for camera {camera_id} in service.")
                except ImportError:
                    # If camera_service is not available, just update local cache
                    logger.warning(f"Camera service not available, updating local cache only")
                    self.camera_active_status_cache[camera_id] = is_currently_active
                    self.cameras[camera_id]["is_active"] = is_currently_active
            else:
                logger.debug(f"Camera {camera_id} status unchanged ({is_currently_active}).")
    
    def _initialize_filter_processors(self):
        """Initialize processors for cameras with specific filters enabled (without rules)"""
        try:
            # Initialize any filter processors here if needed
            # 这部分可以留空，或者根据需要实现
            pass
        except Exception as e:
            logger.error(f"Error initializing filter processors: {str(e)}")
    
    def _process_rules(self):
        """Process all enabled rules"""
        try:
            # Reload the latest data
            self._load_data()
            
            # Process each rule
            for rule_id, rule_data in self.rules.items():
                if not rule_data.get("enabled", False):
                    continue
                
                camera_id = rule_data.get("cameraId")
                event_type = rule_data.get("event")
                
                # Skip if no camera ID or camera doesn't exist
                if not camera_id or camera_id not in self.cameras:
                    continue
                
                camera = self.cameras[camera_id]
                
                # Check if camera's filters have the required filter enabled
                filters_enabled = False
                for filter_config in camera.get("filters", []):
                    if filter_config.get("filter_name", "").lower() == event_type.lower() and filter_config.get("enabled", False):
                        filters_enabled = True
                        break
                
                if not filters_enabled:
                    logger.info(f"Camera {camera_id} does not have the {event_type} filter enabled, skipping rule {rule_id}")
                    continue
                
                # Process based on rule type
                if event_type == "attendance":
                    try:
                        from .processors.attendance_processor import AttendanceProcessor
                        
                        # Get or create attendance processor for this rule
                        if rule_id not in self.active_processors:
                            self.active_processors[rule_id] = AttendanceProcessor(
                                rule_data, 
                                camera, 
                                self.users,
                                self.attendance_dir
                            )
                        
                        # Process the rule
                        self.active_processors[rule_id].process()
                    except ImportError:
                        logger.warning(f"AttendanceProcessor not available, skipping rule {rule_id}")
                
                elif event_type == "authorized_entry":
                    try:
                        from .processors.authorized_entry_processor import AuthorizedEntryProcessor
                        
                        # Get or create authorized entry processor for this rule
                        if rule_id not in self.active_processors:
                            self.active_processors[rule_id] = AuthorizedEntryProcessor(
                                rule_data, 
                                camera, 
                                self.users,
                                self.unauthorized_dir
                            )
                        
                        # Process the rule
                        self.active_processors[rule_id].process()
                    except ImportError:
                        logger.warning(f"AuthorizedEntryProcessor not available, skipping rule {rule_id}")
                
                elif event_type.lower() == "ollamavision":
                    try:
                        from .processors.ai_vision_processor import OllamaVisionProcessor
                        
                        # Get or create Ollama Vision processor for this rule
                        if rule_id not in self.active_processors:
                            self.active_processors[rule_id] = OllamaVisionProcessor(
                                rule_data,
                                camera,
                                self.users,
                                self.unauthorized_dir
                            )
                        
                        # Process the rule
                        self.active_processors[rule_id].process()
                    except ImportError:
                        logger.warning(f"OllamaVisionProcessor not available, skipping rule {rule_id}")
        
        except Exception as e:
            logger.error(f"Error processing rules: {str(e)}", exc_info=True)
    
    def get_attendance_records(self, date=None):
        """Get attendance records for a specific date or all dates"""
        if not date:
            return self.attendance_records
        
        return self.attendance_records.get(date, {})
    
    def get_unauthorized_logs(self, date=None):
        """Get unauthorized entry logs for a specific date or all dates"""
        if not date:
            return self.unauthorized_logs
        
        # Filter logs for the specified date
        date_str = date.strftime("%Y-%m-%d") if isinstance(date, datetime) else str(date)
        date_logs = [log for log in self.unauthorized_logs if log.get("date") == date_str]
        return date_logs
    
    def get_status(self):
        """Get current engine status"""
        return {
            "running": self.running,
            "rules_count": len(self.rules),
            "cameras_count": len(self.cameras),
            "users_count": len(self.users),
            "active_processors": len(self.active_processors),
            "attendance_records_count": len(self.attendance_records),
            "unauthorized_logs_count": len(self.unauthorized_logs)
        }

# 创建全局实例（在 __init__.py 中使用）
# ai_engine = AIEngine()