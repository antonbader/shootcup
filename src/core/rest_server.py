from PyQt6.QtCore import QThread, pyqtSignal
from flask import Flask, request, jsonify
import logging

class RestServerThread(QThread):
    # Signal emitted when a valid request is received: (name, score, type, klasse)
    data_received = pyqtSignal(str, float, str, str)

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.app = Flask(__name__)

        # Disable default flask logging to not clutter the console
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        @self.app.route('/api/score', methods=['POST'])
        def handle_score():
            if not request.is_json:
                return jsonify({"status": "error", "message": "Request body must be JSON"}), 400

            data = request.get_json()

            # Validation
            name = data.get('name')
            score = data.get('score')
            score_type = data.get('type')
            klasse = data.get('klasse')

            if name is None or str(name).strip() == "":
                return jsonify({"status": "error", "message": "Missing required field 'name' or empty"}), 400

            if score is None:
                return jsonify({"status": "error", "message": "Missing required field 'score'"}), 400

            try:
                score = float(score)
            except ValueError:
                return jsonify({"status": "error", "message": "'score' must be a number"}), 400

            if score_type not in ["teiler", "ringzahl"]:
                return jsonify({"status": "error", "message": "'type' must be either 'teiler' or 'ringzahl'"}), 400

            # Optional field parsing
            klasse_str = str(klasse).strip() if klasse is not None else ""

            # Emit signal to main thread
            self.data_received.emit(str(name).strip(), score, score_type, klasse_str)

            return jsonify({"status": "success", "message": "Data added successfully"}), 200

    def run(self):
        # Run flask in this thread.
        # use_reloader=False is required to avoid problems when running in a QThread
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
