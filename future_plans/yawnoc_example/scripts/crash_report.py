import sys
import json

class CrashReporter:
    def __init__(self):
        self.state = {}

    def generate_report(self):
        from .const import VERSION
        
        report = {
            'application': 'yawnoc',
            'version': VERSION,
            'state': self.state,
            'platform': self.get_platform_info(),
            'traceback': self.get_traceback()
        }

        return report
    
    def get_traceback(self):
        try:
            import traceback

            return traceback.format_exc()
        except Exception:
            return 'crashed'
    
    def save_report(self, report):
        f = open('crash_report.json', 'w')
        f.write(json.dumps(report, indent=4))
        f.close()

    def post_report(self, report):
        try:
            import requests

            requests.post('https://dafluffypotato.com/api/crash_report', json=report)

            print('posted crash report')

        except Exception:
            pass

    @property
    def share_allowed(self):
        return '-report' in sys.argv

    def handle_report(self):
        report = self.generate_report()
        self.save_report(report)
        if self.share_allowed:
            self.post_report(report)

    def get_platform_info(self):
        try:
            import platform
            return platform.platform()
        except Exception:
            return 'crashed'

CRASH_REPORTER = CrashReporter()