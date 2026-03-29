"""
HUMAN-READABLE DESCRIPTION:
This file serves as the local HTTP backend. It continuously transmits the exact mathematical piece configurations and move queues over to the local web browser's 3D engine.
"""

"""
server.py
---------
Lightweight HTTP server for the 3D Rubik's Cube visualization.

Provides:
  - Static file serving for the HTML/JS frontend
  - JSON API for cube state and move application

Endpoints:
  GET  /           Serve the 3D viewer (index.html)
  GET  /state      Return current cube state as JSON
  POST /move       Apply a move (body: {"move": "R"})
  POST /scramble   Apply a random scramble (body: {"length": 20, "seed": null})
  POST /reset      Reset cube to solved state
  POST /solve      Solve with Kociemba and return solution

Centers are fixed and never moved by any operation.
"""

import json
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cube import CubieCube
from core.cubie import Color, COLOR_NAMES
from utils.scramble import generate_scramble, scramble_to_string, generate_scramble_at_depth
from solvers.kociemba_solver import solve_with_kociemba
from solvers.ai_solver import RubiksMLP, solve_with_ai
import torch

# Global cube state
_cube = CubieCube()
_move_history = []

# Global AI Model
_ai_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_ai_model(path='data/models/ai_solver.pt'):
    global _ai_model
    if os.path.exists(path):
        _ai_model = RubiksMLP()
        _ai_model.load_state_dict(torch.load(path, map_location=_device))
        _ai_model.to(_device)
        _ai_model.eval()
        print(f"Loaded AI model from {path}")
    else:
        print(f"Warning: AI model not found at {path}")


def get_cube_state_json():
    """Return the current cube state as a JSON-serializable dict."""
    facelet_str = _cube.to_kociemba_string()

    # Map facelet characters to CSS color names (Pure Unshaded Colors)
    color_map = {
        'U': '#FFFFFF',  # White
        'R': '#FF0000',  # Red
        'F': '#00FF00',  # Green
        'D': '#FFFF00',  # Yellow
        'L': '#FF8000',  # Orange
        'B': '#0000FF',  # Blue
    }

    facelets = []
    for ch in facelet_str:
        facelets.append({
            'face': ch,
            'color': color_map[ch],
        })

    return {
        'facelets': facelets,
        'facelet_string': facelet_str,
        'is_solved': _cube.is_solved(),
        'is_legal': _cube.is_legal(),
        'move_history': _move_history,  # Keep full history just in case
        'corner_orientation_sum': sum(_cube.co) % 3,
        'edge_orientation_sum': sum(_cube.eo) % 2,
        'cp': _cube.cp,
        'co': _cube.co,
        'ep': _cube.ep,
        'eo': _cube.eo,
    }


class CubeHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the cube visualization server."""

    def __init__(self, *args, **kwargs):
        # Serve from the visualization directory
        self.viz_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=self.viz_dir, **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/state':
            self._send_json(get_cube_state_json())
        elif parsed.path == '/':
            # Serve index.html
            self.path = '/index.html'
            super().do_GET()
        else:
            super().do_GET()

    def do_POST(self):
        global _cube, _move_history
        parsed = urlparse(self.path)

        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        if parsed.path == '/move':
            move = data.get('move', '')
            try:
                _cube.apply_move(move)
                _move_history.append(move)
                self._send_json({
                    'status': 'ok',
                    'move': move,
                    'state': get_cube_state_json(),
                })
            except ValueError as e:
                self._send_json({'status': 'error', 'message': str(e)}, 400)

        elif parsed.path == '/scramble':
            length = data.get('length', None)
            seed = data.get('seed', None)
            scramble = generate_scramble(length=length, seed=seed)
            _cube = CubieCube()
            _cube.apply_sequence(scramble)
            _move_history = list(scramble)
            self._send_json({
                'status': 'ok',
                'scramble': scramble_to_string(scramble),
                'state': get_cube_state_json(),
            })

        elif parsed.path == '/reset':
            _cube = CubieCube()
            _move_history = []
            self._send_json({
                'status': 'ok',
                'state': get_cube_state_json(),
            })

        elif parsed.path == '/solve':
            result = solve_with_kociemba(_cube)
            if result['error'] is None and result['validated']:
                solution_moves = result['solution'].split()
                _cube.apply_sequence(solution_moves)
                _move_history.extend(solution_moves)
            self._send_json({
                'status': 'ok' if result['error'] is None else 'error',
                'solution': result['solution'],
                'num_moves': result['num_moves'],
                'solve_time': result['solve_time'],
                'validated': result['validated'],
                'state': get_cube_state_json(),
            })

        elif parsed.path == '/solve_ai':
            if _ai_model is None:
                self._send_json({'status': 'error', 'message': 'AI model not loaded'}, 400)
                return

            result = solve_with_ai(_cube, _ai_model, device=_device)
            if result['solved']:
                _cube.apply_sequence(result['solution'])
                _move_history.extend(result['solution'])

            self._send_json({
                'status': 'ok' if result['solved'] else 'fail',
                'solution': ' '.join(result['solution']),
                'num_moves': result['num_moves'],
                'solve_time': result['solve_time'],
                'confidences': result['confidences'],
                'state': get_cube_state_json(),
            })

        elif parsed.path == '/compare_benchmark':
            if _ai_model is None:
                self._send_json({'status': 'error', 'message': 'AI model not loaded'}, 400)
                return

            # Run a quick benchmark (5 tests per depth, up to depth 5)
            # This is synchronous but small enough for a local viz tool
            import statistics
            benchmark_results = []
            for depth in range(1, 6):
                ai_solved = 0
                koc_solved = 0
                ai_times = []
                koc_times = []

                for _ in range(5):
                    scramble = generate_scramble_at_depth(depth)
                    test_cube = CubieCube()
                    test_cube.apply_sequence(scramble)

                    # Kociemba
                    k_res = solve_with_kociemba(test_cube)
                    if k_res['error'] is None:
                        koc_solved += 1
                        koc_times.append(k_res['solve_time'])

                    # AI
                    a_res = solve_with_ai(test_cube, _ai_model, device=_device)
                    if a_res['solved']:
                        ai_solved += 1
                        ai_times.append(a_res['solve_time'])

                benchmark_results.append({
                    'depth': depth,
                    'ai_rate': ai_solved / 5,
                    'koc_rate': koc_solved / 5,
                    'ai_avg_time': statistics.mean(ai_times) if ai_times else 0,
                    'koc_avg_time': statistics.mean(koc_times) if koc_times else 0,
                })

            self._send_json({
                'status': 'ok',
                'results': benchmark_results
            })

        else:
            self._send_json({'status': 'error', 'message': 'Unknown endpoint'}, 404)

    def _send_json(self, data, status=200):
        response = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging for cleaner output."""
        pass


def start_server(port=8080):
    """Start the visualization server."""
    load_ai_model()
    server = HTTPServer(('localhost', port), CubeHandler)
    print(f"Rubik's Cube 3D Visualization Server")
    print(f"Open http://localhost:{port} in your browser")
    print(f"Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Rubik's Cube visualization server")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    args = parser.parse_args()
    start_server(port=args.port)
